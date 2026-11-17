from typing import Literal
import joblib
import pandas as pd

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.config import MODEL_PATH
from app.review_storage import initialize_database, save_review

app = FastAPI(
    title="Fraud Risk Assessment API",
    description="An AI-powered fraud risk assessment system with human oversight.",
    version="1.0.0"
)

# Load the trained model
model = joblib.load(MODEL_PATH)
initialize_database()

# Expected transaction features
FEATURES = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


class Transaction(BaseModel):
    features: list[float] = Field(..., min_length=30, max_length=30)

class Review(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    fraud_probability: float = Field(..., ge=0, le=1)
    decision: Literal[
    "Suspected Fraud",
    "Legitimate",
    "Needs Further Investigation"
]
    notes: str | None = None

@app.get("/")
def home():
    return {
        "message": "Fraud Risk Assessment API is running."
    }


@app.post("/predict")
def assess_transaction(transaction: Transaction):

    input_data = pd.DataFrame(
        [transaction.features],
        columns=FEATURES
    )

@app.post("/reviews")
def submit_review(review: Review):

    review_id = save_review(
        transaction_id=review.transaction_id,
        fraud_probability=review.fraud_probability,
        decision=review.decision,
        notes=review.notes
    )

    return {
        "message": "Human review saved successfully.",
        "review_id": review_id,
        "transaction_id": review.transaction_id,
        "decision": review.decision
    }

    # Obtain the model-estimated fraud probability
    probability = model.predict_proba(input_data)[0][1]

    # Assign a descriptive risk category
    if probability < 0.30:
        risk_level = "Low"
    elif probability < 0.70:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "fraud_probability": round(float(probability), 4),
        "risk_percentage": round(float(probability) * 100, 2),
        "risk_level": risk_level,
        "message": "This is a model-generated risk assessment, not a confirmed fraud decision."
    }
