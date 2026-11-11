
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    roc_auc_score,
    confusion_matrix
)

from src.train import DECISION_THRESHOLD


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the fitted model using the selected decision threshold.

    Returns:
        dict: Evaluation metrics and confusion matrix values.
    """

    # Generate fraud probabilities
    y_prob = model.predict_proba(X_test)[:, 1]

    # Apply the selected decision threshold
    y_pred = (y_prob >= DECISION_THRESHOLD).astype(int)

    # Calculate classification metrics
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(
            precision_score(y_test, y_pred, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, y_pred, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_test, y_pred, zero_division=0)
        ),
        "average_precision": float(
            average_precision_score(y_test, y_prob)
        ),
        "roc_auc": float(
            roc_auc_score(y_test, y_prob)
        )
    }

    # Extract confusion matrix values
    tn, fp, fn, tp = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1]
    ).ravel()

    confusion_matrix_results = {
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp)
    }

    return {
        "metrics": metrics,
        "confusion_matrix": confusion_matrix_results,
        "decision_threshold": DECISION_THRESHOLD
    }
