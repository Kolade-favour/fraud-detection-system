from pathlib import Path
import json

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Project directories
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

# Saved model
MODEL_PATH = MODEL_DIR / "rf_smote_model.pkl"

# Saved classification threshold
THRESHOLD_PATH = MODEL_DIR / "threshold.json"

# Load threshold
with open(THRESHOLD_PATH, "r") as f:
    THRESHOLD = json.load(f)["threshold"]