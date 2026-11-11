
import json
import mlflow
import mlflow.sklearn

from pathlib import Path


class MLflowManager:
    """
    Manage MLflow experiment tracking and model registration.
    """

    def __init__(
        self,
        experiment_name="Fraud Detection Training",
        tracking_uri="sqlite:///mlflow.db",
        model_name="fraud-detection-xgboost"
    ):
        self.experiment_name = experiment_name
        self.model_name = model_name

        mlflow.set_tracking_uri(tracking_uri)

        experiment = mlflow.set_experiment(experiment_name)

        self.experiment_id = experiment.experiment_id

    def start_run(self, run_name=None):
        """Start an MLflow training run."""

        return mlflow.start_run(
            experiment_id=self.experiment_id,
            run_name=run_name
        )

    def log_params(self, params):
        """Log model configuration and training parameters."""

        mlflow.log_params(params)

    def log_metrics(self, metrics):
        """Log evaluation metrics."""

        mlflow.log_metrics(metrics)

    def log_confusion_matrix(self, confusion_matrix):
        """Log confusion matrix values."""

        mlflow.log_metrics(confusion_matrix)

    def log_model(self, model, metadata):
        """
        Log and register the fitted model using cloudpickle.
        """

        metadata_path = Path("model_metadata.json")

        try:
            metadata_path.write_text(
                json.dumps(metadata, indent=4)
            )

            mlflow.log_artifact(str(metadata_path))

            model_info = mlflow.sklearn.log_model(
                sk_model=model,
                name="fraud_detection_pipeline",
                registered_model_name=self.model_name,
                serialization_format="cloudpickle"
            )

            return model_info

        finally:
            metadata_path.unlink(missing_ok=True)


    def load_model(self, model_uri):
        """
        Load a previously registered MLflow model.

        Args:
            model_uri: URI identifying the exact registered model.

        Returns:
            Loaded fitted model.
        """

        try:
            model = mlflow.sklearn.load_model(model_uri)

            print(f"Successfully loaded model: {model_uri}")

            return model

        except Exception as e:
            raise RuntimeError(
                f"Failed to load MLflow model: {e}"
            ) from e
