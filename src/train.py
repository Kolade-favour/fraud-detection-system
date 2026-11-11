
import numpy as np
import mlflow

from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.utils.validation import check_is_fitted

from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline as ImbPipeline

from src.mlflow_manager import MLflowManager


RANDOM_STATE = 42
DECISION_THRESHOLD = 0.30
TEST_SIZE = 0.2

MODEL_NAME = "fraud-detection-xgboost"
IMBALANCE_STRATEGY = "Class Weighting"


# Selected hyperparameters from RandomizedSearchCV
XGBOOST_PARAMS = {
    "n_estimators": 443,
    "max_depth": 7,
    "learning_rate": 0.0703,
    "subsample": 0.7545,
    "colsample_bytree": 0.8001,
    "min_child_weight": 2,
    "gamma": 0.7143,
    "reg_alpha": 1.4528,
    "reg_lambda": 0.2659,
    "random_state": RANDOM_STATE,
    "eval_metric": "logloss",
    "n_jobs": 1
}


class ClassWeightedClassifier(ClassifierMixin, BaseEstimator):
    """
    Apply balanced class weighting to XGBoost.
    """

    def __init__(self, estimator):
        self.estimator = estimator

    def fit(self, X, y):

        self.estimator_ = clone(self.estimator)

        # Count legitimate and fraudulent transactions
        class_counts = np.bincount(
            np.asarray(y, dtype=int)
        )

        if len(class_counts) != 2 or np.any(class_counts == 0):
            raise ValueError(
                "Training data must contain both target classes."
            )

        # Calculate class imbalance ratio
        scale_pos_weight = class_counts[0] / class_counts[1]

        # Apply class weighting
        self.estimator_.set_params(
            scale_pos_weight=scale_pos_weight
        )

        # Train XGBoost
        self.estimator_.fit(X, y)

        self.classes_ = self.estimator_.classes_

        return self

    def predict(self, X):
        check_is_fitted(self, "estimator_")
        return self.estimator_.predict(X)

    def predict_proba(self, X):
        check_is_fitted(self, "estimator_")
        return self.estimator_.predict_proba(X)


def build_model_pipeline():
    """
    Build the selected class-weighted XGBoost pipeline.
    """

    xgb_model = XGBClassifier(**XGBOOST_PARAMS)

    weighted_model = ClassWeightedClassifier(
        estimator=xgb_model
    )

    pipeline = ImbPipeline(
        steps=[
            ("classifier", weighted_model)
        ]
    )

    return pipeline


def train_model(X_train, y_train):
    """
    Train the selected XGBoost pipeline.
    """

    model = build_model_pipeline()

    model.fit(X_train, y_train)

    scale_pos_weight = (
        model.named_steps["classifier"]
        .estimator_.scale_pos_weight
    )

    print("\nXGBoost training completed.")
    print(f"Training records: {len(X_train):,}")
    print(f"Class weighting: {scale_pos_weight:.4f}")

    return model


def run_training():
    """
    Execute the complete training and MLflow workflow.

    Returns:
        dict: Fitted model, evaluation results and MLflow information.
    """

    # Import locally to avoid circular imports.
    from src.data_prep import (
        load_and_clean_data,
        prepare_train_test_data
    )

    from src.evaluate import evaluate_model

    # Initialize MLflow manager
    mlflow_manager = MLflowManager(
        experiment_name="Fraud Detection Training",
        model_name=MODEL_NAME
    )

    # Start MLflow run before training
    with mlflow_manager.start_run(
        run_name="Tuned XGBoost Training"
    ) as active_run:

        print("\nStarting training workflow...")

        # 1. Load and prepare data
        df = load_and_clean_data()

        X_train, X_test, y_train, y_test = (
            prepare_train_test_data(df)
        )

        # 2. Collect training parameters
        params = {
            **XGBOOST_PARAMS,
            "model_type": "XGBoost",
            "imbalance_strategy": IMBALANCE_STRATEGY,
            "decision_threshold": DECISION_THRESHOLD,
            "random_state": RANDOM_STATE,
            "test_size": TEST_SIZE,
            "training_records": len(X_train),
            "testing_records": len(X_test),
            "feature_count": X_train.shape[1]
        }

        mlflow_manager.log_params(params)

        # 3. Train model
        model = train_model(X_train, y_train)

        # 4. Evaluate model
        evaluation_results = evaluate_model(
            model=model,
            X_test=X_test,
            y_test=y_test
        )

        metrics = evaluation_results["metrics"]

        confusion_matrix_results = (
            evaluation_results["confusion_matrix"]
        )

        # 5. Log evaluation metrics
        mlflow_manager.log_metrics(metrics)

        # 6. Log confusion matrix values
        mlflow_manager.log_confusion_matrix(
            confusion_matrix_results
        )

        # 7. Prepare model metadata for inference
        metadata = {
            "model_name": MODEL_NAME,
            "model_type": "XGBoost",
            "imbalance_strategy": IMBALANCE_STRATEGY,
            "decision_threshold": DECISION_THRESHOLD,
            "random_state": RANDOM_STATE,
            "feature_names": list(X_train.columns),
            "target_name": "Class",
            "model_parameters": XGBOOST_PARAMS
        }

        # 8. Log and register fitted model
        model_info = mlflow_manager.log_model(
            model=model,
            metadata=metadata
        )

        run_id = active_run.info.run_id

        print("\nTRAINING WORKFLOW COMPLETED")
        print("=" * 45)
        print(f"MLflow Run ID: {run_id}")
        print(f"Model Name: {MODEL_NAME}")
        print(f"Model URI: {model_info.model_uri}")

        # 9. Return training results
        return {
            "model": model,
            "evaluation": evaluation_results,
            "run_id": run_id,
            "model_uri": model_info.model_uri,
            "metadata": metadata
        }

if __name__ == "__main__":
    results = run_training()

    print("\nTRAINING SUMMARY")
    print("=" * 40)

    print(f"Run ID: {results['run_id']}")
    print(f"Model URI: {results['model_uri']}")

    print("\nEvaluation Metrics:")

    for metric, value in results["evaluation"]["metrics"].items():
        print(f"{metric}: {value:.4f}")
