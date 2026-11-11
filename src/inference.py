from src.database.database import get_database_connection
import pandas as pd
import json
import shap
import numpy as np
from scipy.special import expit
from datetime import datetime, timezone
from src.database.database import get_database_connection
from src.mlflow_manager import MLflowManager



MODEL_VERSION = "m-94561d74a8de49369f120cdc81b9b98d"
MODEL_URI = f"models:/{MODEL_VERSION}"

DECISION_THRESHOLD = 0.30


def claim_pending_transactions(batch_size=100):
    """
    Claim pending simulation events for inference.

    Locks selected events, changes their status to processing,
    and retrieves their original transaction features.

    Args:
        batch_size: Maximum number of events to claim.

    Returns:
        list: Claimed transactions with their original features.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    connection = get_database_connection()

    if connection is None:
        raise ConnectionError("Could not connect to the database.")

    cursor = None

    try:
        # Start a database transaction
        connection.start_transaction()

        cursor = connection.cursor(dictionary=True)

        # Select and lock pending events
        query = """
            SELECT
                s.simulation_id,
                s.source_record_id,
                r.`Time`,
                r.`V1`, r.`V2`, r.`V3`, r.`V4`,
                r.`V5`, r.`V6`, r.`V7`, r.`V8`,
                r.`V9`, r.`V10`, r.`V11`, r.`V12`,
                r.`V13`, r.`V14`, r.`V15`, r.`V16`,
                r.`V17`, r.`V18`, r.`V19`, r.`V20`,
                r.`V21`, r.`V22`, r.`V23`, r.`V24`,
                r.`V25`, r.`V26`, r.`V27`, r.`V28`,
                r.`Amount`

            FROM simulated_transactions AS s

            INNER JOIN raw_transactions AS r
                ON s.source_record_id = r.source_record_id

            WHERE s.processing_status = 'pending'

            ORDER BY s.simulation_id ASC

            LIMIT %s

            FOR UPDATE OF s SKIP LOCKED
        """

        cursor.execute(query, (batch_size,))

        transactions = cursor.fetchall()

        if not transactions:
            connection.commit()
            return []

        # Extract selected simulation IDs
        simulation_ids = [
            transaction["simulation_id"]
            for transaction in transactions
        ]

        placeholders = ", ".join(
            ["%s"] * len(simulation_ids)
        )

        # Claim the selected events
        update_query = f"""
            UPDATE simulated_transactions
            SET processing_status = 'processing'
            WHERE simulation_id IN ({placeholders})
              AND processing_status = 'pending'
        """

        cursor.execute(update_query, simulation_ids)

        if cursor.rowcount != len(simulation_ids):
            raise RuntimeError(
                "Not all selected events were successfully claimed."
            )

        # Commit the status changes
        connection.commit()

        return transactions

    except Exception as e:
        connection.rollback()
        raise RuntimeError(
            f"Failed to claim pending transactions: {e}"
        ) from e

    finally:
        if cursor:
            cursor.close()

        connection.close()



def fetch_processing_transactions(batch_size=100):
    """
    Retrieve events already claimed by the inference service.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    connection = get_database_connection()

    if connection is None:
        raise ConnectionError("Could not connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        columns = [
            "s.simulation_id",
            "s.source_record_id",
            "r.`Time`"
        ]

        columns += [f"r.`V{i}`" for i in range(1, 29)]
        columns += ["r.`Amount`"]

        query = f"""
            SELECT {", ".join(columns)}
            FROM simulated_transactions AS s
            INNER JOIN raw_transactions AS r
                ON s.source_record_id = r.source_record_id
            WHERE s.processing_status = 'processing'
            ORDER BY s.simulation_id ASC
            LIMIT %s
        """

        cursor.execute(query, (batch_size,))

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        connection.close()


def load_inference_model():
    """
    Load the selected registered XGBoost pipeline from MLflow.
    """

    manager = MLflowManager()

    model = manager.load_model(MODEL_URI)

    return model

def load_shap_explainer(model):
    """
    Initialize a SHAP TreeExplainer for the registered XGBoost model.
    """

    xgb_model = (
        model.named_steps["classifier"].estimator_
    )

    explainer = shap.TreeExplainer(xgb_model)

    print("SHAP explainer initialized successfully.")

    return explainer



def generate_predictions(transactions, model, explainer=None):
    """
    Generate enriched prediction results for the dashboard.

    The model generates probabilities. The inference service
    adds transaction identifiers, classification and metadata.

    SHAP explanations will be added in a later stage.
    """

    if not transactions:
        return []

    feature_columns = (
        ["Time"]
        + [f"V{i}" for i in range(1, 29)]
        + ["Amount"]
    )

    # Prepare exactly the 30 features used during training
    X = pd.DataFrame(
        [
            {
                column: transaction[column]
                for column in feature_columns
            }
            for transaction in transactions
        ],
        columns=feature_columns
    )

    # Generate probabilities using the fitted pipeline
    probabilities = model.predict_proba(X)

    # Calculate SHAP explanations for the entire batch
    shap_results = explainer(X)

    shap_array = shap_results.values

    # Identify the probability column corresponding to fraud
    fraud_class_index = list(model.classes_).index(1)

    fraud_probabilities = probabilities[:, fraud_class_index]

    legitimate_probabilities = 1 - fraud_probabilities

    # Apply the existing classification threshold
    predicted_classes = (
        fraud_probabilities >= DECISION_THRESHOLD
    ).astype(int)

    # Generate enriched prediction records
    results = []

    for i, transaction in enumerate(transactions):

        # Get SHAP contributions for this transaction
        transaction_shap = shap_array[i]

        # Rank features by absolute SHAP contribution
        top_indices = np.argsort(
            np.abs(transaction_shap)
        )[::-1][:10]

        top_features = [
            {
                "feature": feature_columns[j],
                "feature_value": float(X.iloc[i, j]),
                "shap_value": float(transaction_shap[j])
            }
            for j in top_indices
            ]


        shap_data = {
            "base_value": float(shap_results.base_values[i]),
            "shap_values": [
                {
                    "feature": feature_columns[j],
                    "feature_value": float(X.iloc[i, j]),
                    "shap_value": float(transaction_shap[j])
                }
                for j in range(len(feature_columns))
            ]
        }

        results.append({
            # Transaction identifiers
            "simulation_id": transaction["simulation_id"],
            "source_record_id": transaction["source_record_id"],

            # Original transaction details
            "Time": float(transaction["Time"]),
            "Amount": float(transaction["Amount"]),

            # Model prediction
            "legitimate_probability": float(
                legitimate_probabilities[i]
            ),
            "fraud_probability": float(
                fraud_probabilities[i]
            ),

            # Inference metadata
            "decision_threshold_used": DECISION_THRESHOLD,
            "predicted_class": int(predicted_classes[i]),
            "model_version": MODEL_VERSION,
            "prediction_timestamp": datetime.now(
                timezone.utc
            ).replace(tzinfo=None),

            # Reserved for risk policy and SHAP implementation
            "risk_level": "unassigned",
            "top_features": top_features,
            "shap_values": shap_data,
            "explanation": None
        })

    return results



def save_predictions(predictions):
    """
    Save prediction results and mark simulation events as processed.

    Both operations happen in one database transaction.

    Args:
        predictions: List of enriched prediction dictionaries.

    Returns:
        int: Number of successfully saved predictions.
    """

    if not predictions:
        return 0

    connection = get_database_connection()

    if connection is None:
        raise ConnectionError("Could not connect to the database.")

    cursor = None

    try:
        connection.start_transaction()
        cursor = connection.cursor()

        # 1. Prepare prediction records
        insert_query = """
            INSERT INTO prediction_results (
                simulation_id,
                model_version,
                prediction_timestamp,
                legitimate_probability,
                fraud_probability,
                decision_threshold_used,
                predicted_class,
                risk_level,
                top_features,
                shap_values,
                explanation
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """

        records = []

        simulation_ids = []

        for prediction in predictions:

            simulation_ids.append(prediction["simulation_id"])

            records.append((
                prediction["simulation_id"],
                prediction["model_version"],
                prediction["prediction_timestamp"],
                prediction["legitimate_probability"],
                prediction["fraud_probability"],
                prediction["decision_threshold_used"],
                prediction["predicted_class"],
                prediction["risk_level"],
                json.dumps(prediction["top_features"])
                if prediction["top_features"] is not None else None,
                json.dumps(prediction["shap_values"])
                if prediction["shap_values"] is not None else None,
                prediction["explanation"]
            ))

        # Prevent accidental duplicate event IDs in this batch
        if len(simulation_ids) != len(set(simulation_ids)):
            raise ValueError(
                "Duplicate simulation IDs found in prediction batch."
            )

        # 2. Insert predictions
        cursor.executemany(insert_query, records)

        # 3. Update simulation event statuses
        placeholders = ", ".join(
            ["%s"] * len(simulation_ids)
        )

        update_query = f"""
            UPDATE simulated_transactions
            SET
                processing_status = 'processed',
                processed_at = CURRENT_TIMESTAMP(6)
            WHERE simulation_id IN ({placeholders})
              AND processing_status = 'processing'
        """

        cursor.execute(update_query, simulation_ids)

        if cursor.rowcount != len(simulation_ids):
            raise RuntimeError(
                "Not all simulation events were updated to processed."
            )

        # 4. Commit both operations
        connection.commit()

        print(
            f"Successfully saved {len(predictions)} predictions."
        )

        return len(predictions)

    except Exception as e:
        connection.rollback()

        raise RuntimeError(
            f"Prediction persistence failed: {e}"
        ) from e

    finally:
        if cursor:
            cursor.close()

        connection.close()



def mark_transactions_failed(simulation_ids):
    """
    Mark claimed simulation events as failed.

    Used when prediction generation or persistence fails.
    """

    if not simulation_ids:
        return 0

    connection = get_database_connection()

    if connection is None:
        raise ConnectionError("Could not connect to the database.")

    cursor = None

    try:
        connection.start_transaction()
        cursor = connection.cursor()

        placeholders = ", ".join(
            ["%s"] * len(simulation_ids)
        )

        query = f"""
            UPDATE simulated_transactions
            SET processing_status = 'failed'
            WHERE simulation_id IN ({placeholders})
              AND processing_status = 'processing'
        """

        cursor.execute(query, simulation_ids)

        updated_count = cursor.rowcount

        connection.commit()

        return updated_count

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        connection.close()



def run_inference(
    max_transactions=1000,
    batch_size=100,
    max_runtime_seconds=300
):
    """
    Run a bounded inference execution cycle.

    Loads the registered model once, claims pending events,
    generates predictions, and saves results.

    Args:
        max_transactions: Maximum events to attempt per execution.
        batch_size: Maximum events to process per batch.
        max_runtime_seconds: Maximum execution time in seconds.

    Returns:
        dict: Inference execution statistics.
    """

    import time

    # 1. Validate execution limits
    if max_transactions <= 0 or batch_size <= 0:
        raise ValueError(
            "Transaction limits must be greater than zero."
        )

    if max_runtime_seconds <= 0:
        raise ValueError(
            "Runtime must be greater than zero."
        )

    # 2. Initialize execution statistics
    start_timestamp = time.monotonic()

    records_claimed = 0
    predictions_saved = 0
    failed_events = 0
    batches_processed = 0

    print("Starting inference execution...")

    # 3. Load the model and SHAP explainer once
    model = load_inference_model()

    explainer = load_shap_explainer(model)

    print("Inference model and SHAP explainer are ready.")

    print("Inference model is ready.")

    # 4. Main inference loop
    while records_claimed < max_transactions:

        elapsed_time = time.monotonic() - start_timestamp

        if elapsed_time >= max_runtime_seconds:
            print("Maximum inference runtime reached.")
            break

        # Determine remaining execution capacity
        remaining = max_transactions - records_claimed

        current_batch_size = min(batch_size, remaining)

        # 5. Claim pending events
        transactions = claim_pending_transactions(
            batch_size=current_batch_size
        )

        # Stop if there are no pending events
        if not transactions:
            print("No pending events available.")
            break

        simulation_ids = [
            transaction["simulation_id"]
            for transaction in transactions
        ]

        records_claimed += len(transactions)

        try:
            # 6. Generate predictions
            predictions = generate_predictions(
                transactions,
                model,
                explainer=explainer
            )

            # 7. Save predictions and mark events processed
            saved = save_predictions(predictions)

            predictions_saved += saved
            batches_processed += 1

            print(
                f"Batch {batches_processed} completed | "
                f"Claimed: {len(transactions)} | "
                f"Saved: {saved}"
            )

        except Exception as e:

            print(f"Inference batch failed: {e}")

            # 8. Mark affected events as failed
            try:
                updated = mark_transactions_failed(
                    simulation_ids
                )

                failed_events += updated

                print(
                    f"Marked {updated} events as failed."
                )

            except Exception as failure_error:

                print(
                    "Could not update failed event statuses: "
                    f"{failure_error}"
                )

                print(
                    "These events may remain in processing "
                    "and require recovery."
                )

                failed_events += len(simulation_ids)

            # Stop this execution after a failed batch
            break

    # 9. Calculate execution time
    elapsed_time = time.monotonic() - start_timestamp

    # 10. Display execution summary
    print("\nInference execution completed.")
    print(f"Events claimed: {records_claimed}")
    print(f"Predictions saved: {predictions_saved}")
    print(f"Failed events: {failed_events}")
    print(f"Batches processed: {batches_processed}")
    print(f"Runtime: {elapsed_time:.2f} seconds")

    return {
        "records_claimed": records_claimed,
        "predictions_saved": predictions_saved,
        "failed_events": failed_events,
        "batches_processed": batches_processed,
        "elapsed_seconds": elapsed_time
    }
