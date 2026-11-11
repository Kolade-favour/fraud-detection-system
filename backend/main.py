
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, Query
from src.database.database import get_database_connection
from backend.schemas import AnalystDecisionCreate

# Initialize FastAPI application
app = FastAPI(
    title="Fraud Detection API",
    description="API for the Real-Time Fraud Detection System",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Fraud Detection API is running",
        "status": "online"
    }


@app.get("/health")
def health_check():

    connection = None
    cursor = None

    try:
        connection = get_database_connection()

        if connection is None:
            raise ConnectionError("Database connection failed.")

        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()

        return {
            "api_status": "healthy",
            "database_status": "connected"
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "api_status": "available",
                "database_status": "disconnected",
                "error": str(e)
            }
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()




@app.get("/dashboard/summary")
def dashboard_summary():

    connection = None
    cursor = None

    try:
        connection = get_database_connection()

        if connection is None:
            raise ConnectionError("Database connection failed.")

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT

                (SELECT COUNT(*)
                 FROM raw_transactions)
                AS total_raw_transactions,

                (SELECT COUNT(*)
                 FROM simulated_transactions)
                AS total_simulated_transactions,

                (SELECT COUNT(*)
                 FROM prediction_results)
                AS total_predictions,

                (SELECT COUNT(*)
                 FROM prediction_results
                 WHERE predicted_class = 1)
                AS fraud_predictions,

                (SELECT COUNT(*)
                 FROM prediction_results
                 WHERE predicted_class = 0)
                AS legitimate_predictions,

                (SELECT COUNT(*)
                 FROM simulated_transactions
                 WHERE processing_status = 'pending')
                AS pending_transactions,

                (SELECT COUNT(*)
                 FROM simulated_transactions
                 WHERE processing_status = 'failed')
                AS failed_transactions,

                (SELECT COUNT(*)
                 FROM analyst_decisions
                 WHERE analyst_outcome = 'confirmed_fraud')
                AS confirmed_fraud_cases
        """

        cursor.execute(query)

        result = cursor.fetchone()

        return {
            "status": "success",
            "dashboard_summary": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard summary: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()




@app.get("/alerts")
def get_fraud_alerts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):

    connection = None
    cursor = None

    try:
        connection = get_database_connection()

        if connection is None:
            raise ConnectionError("Database connection failed.")

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                p.prediction_id,
                s.simulation_id,
                s.source_record_id,
                r.Amount AS amount,
                r.Time AS transaction_time,
                p.fraud_probability,
                p.legitimate_probability,
                p.predicted_class,
                p.decision_threshold_used,
                p.model_version,
                p.prediction_timestamp,
                p.risk_level,

                (
                    SELECT ad.analyst_outcome
                    FROM analyst_decisions ad
                    WHERE ad.prediction_id = p.prediction_id
                    ORDER BY
                        ad.decision_timestamp DESC,
                        ad.decision_id DESC
                    LIMIT 1
                ) AS analyst_outcome,

                (
                    SELECT ad.reviewer
                    FROM analyst_decisions ad
                    WHERE ad.prediction_id = p.prediction_id
                    ORDER BY
                        ad.decision_timestamp DESC,
                        ad.decision_id DESC
                    LIMIT 1
                ) AS reviewer

            FROM prediction_results p

            JOIN simulated_transactions s
                ON p.simulation_id = s.simulation_id

            JOIN raw_transactions r
                ON s.source_record_id = r.source_record_id

            WHERE p.predicted_class = 1

            ORDER BY
                p.prediction_timestamp DESC,
                p.prediction_id DESC

            LIMIT %s OFFSET %s
        """

        cursor.execute(query, (limit, offset))

        alerts = cursor.fetchall()

        return {
            "status": "success",
            "total_returned": len(alerts),
            "limit": limit,
            "offset": offset,
            "alerts": alerts
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve fraud alerts: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()



@app.get("/alerts/{prediction_id}")
def investigate_alert(prediction_id: int):

    connection = None
    cursor = None

    try:
        connection = get_database_connection()

        if connection is None:
            raise ConnectionError("Database connection failed.")

        cursor = connection.cursor(dictionary=True)

        # Retrieve transaction and prediction details
        query = """
            SELECT
                p.prediction_id,
                p.model_version,
                p.prediction_timestamp,
                p.legitimate_probability,
                p.fraud_probability,
                p.decision_threshold_used,
                p.predicted_class,
                p.risk_level,
                p.top_features,
                p.shap_values,
                p.explanation,

                s.simulation_id,
                s.source_record_id,
                s.replayed_at,
                s.processing_status,

                r.Time AS transaction_time,
                r.Amount AS amount,

                r.V1, r.V2, r.V3, r.V4,
                r.V5, r.V6, r.V7, r.V8,
                r.V9, r.V10, r.V11, r.V12,
                r.V13, r.V14, r.V15, r.V16,
                r.V17, r.V18, r.V19, r.V20,
                r.V21, r.V22, r.V23, r.V24,
                r.V25, r.V26, r.V27, r.V28

            FROM prediction_results p

            JOIN simulated_transactions s
                ON p.simulation_id = s.simulation_id

            JOIN raw_transactions r
                ON s.source_record_id = r.source_record_id

            WHERE p.prediction_id = %s
        """

        cursor.execute(query, (prediction_id,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Prediction not found."
            )

        # Separate transaction details
        transaction = {
            "simulation_id": result["simulation_id"],
            "source_record_id": result["source_record_id"],
            "replayed_at": result["replayed_at"],
            "processing_status": result["processing_status"],
            "transaction_time": result["transaction_time"],
            "amount": result["amount"],
            "features": {
                f"V{i}": result[f"V{i}"]
                for i in range(1, 29)
            }
        }

        # Separate model prediction details
        prediction = {
            "prediction_id": result["prediction_id"],
            "model_version": result["model_version"],
            "prediction_timestamp": result["prediction_timestamp"],
            "legitimate_probability": result["legitimate_probability"],
            "fraud_probability": result["fraud_probability"],
            "decision_threshold_used": result["decision_threshold_used"],
            "predicted_class": result["predicted_class"],
            "risk_level": result["risk_level"],
            "top_features": result["top_features"],
            "shap_values": result["shap_values"],
            "explanation": result["explanation"]
        }

        # Retrieve analyst decision history
        decision_query = """
            SELECT
                decision_id,
                analyst_outcome,
                notes,
                reviewer,
                decision_timestamp

            FROM analyst_decisions

            WHERE prediction_id = %s

            ORDER BY decision_timestamp DESC, decision_id DESC
        """

        cursor.execute(decision_query, (prediction_id,))
        analyst_history = cursor.fetchall()

        return {
            "status": "success",
            "transaction": transaction,
            "prediction": prediction,
            "analyst_history": analyst_history
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve investigation details: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()



@app.post("/decisions", status_code=201)
def create_analyst_decision(decision: AnalystDecisionCreate):

    connection = None
    cursor = None

    try:
        connection = get_database_connection()

        if connection is None:
            raise ConnectionError("Database connection failed.")

        cursor = connection.cursor(dictionary=True)

        # 1. Verify that the prediction exists
        cursor.execute(
            """
            SELECT prediction_id
            FROM prediction_results
            WHERE prediction_id = %s
            """,
            (decision.prediction_id,)
        )

        prediction = cursor.fetchone()

        if prediction is None:
            raise HTTPException(
                status_code=404,
                detail="Prediction not found."
            )

        # 2. Insert a new analyst decision
        insert_query = """
            INSERT INTO analyst_decisions (
                prediction_id,
                analyst_outcome,
                notes,
                reviewer
            )
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            insert_query,
            (
                decision.prediction_id,
                decision.analyst_outcome,
                decision.notes,
                decision.reviewer
            )
        )

        decision_id = cursor.lastrowid

        # 3. Commit the decision
        connection.commit()

        return {
            "status": "success",
            "message": "Analyst decision recorded successfully.",
            "decision": {
                "decision_id": decision_id,
                "prediction_id": decision.prediction_id,
                "analyst_outcome": decision.analyst_outcome,
                "notes": decision.notes,
                "reviewer": decision.reviewer
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        if connection:
            connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to record analyst decision: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
