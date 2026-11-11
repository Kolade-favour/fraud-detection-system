
from typing import Literal

from pydantic import BaseModel, Field


class AnalystDecisionCreate(BaseModel):

    prediction_id: int = Field(gt=0)

    analyst_outcome: Literal[
        "confirmed_fraud",
        "legitimate",
        "inconclusive",
        "pending"
    ]

    notes: str | None = Field(default=None, max_length=2000)

    reviewer: str | None = Field(default=None, max_length=100)
