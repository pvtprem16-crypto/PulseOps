from pathlib import Path

import joblib
import pandas as pd

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/ml",
    tags=["ML Prediction"]
)

# --------------------------------------------------
# PATHS & MODEL LOADING
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "ml" / "models" / "balanced_random_forest.pkl"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"ML model not found: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# INPUT SCHEMA
# --------------------------------------------------

class TicketPredictionInput(BaseModel):
    priority: str
    client: str
    service: str
    category: str
    subcategory: str
    assigned_team: str
    channel: str

    created_hour: int = Field(ge=0, le=23)
    created_day_of_week: int = Field(ge=0, le=6)
    created_month: int = Field(ge=1, le=12)


# --------------------------------------------------
# PREDICTION ENDPOINT
# --------------------------------------------------

@router.post("/predict")
def predict_sla_breach(ticket: TicketPredictionInput):

    try:
        input_data = pd.DataFrame([ticket.model_dump()])

        probabilities = model.predict_proba(input_data)[0]

        # Class 1 represents SLA breach
        breach_probability = float(probabilities[1])

        if breach_probability >= 0.75:
            risk_level = "High"
        elif breach_probability >= 0.50:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        return {
            "sla_breach_probability": round(breach_probability, 4),
            "sla_breach_percentage": round(breach_probability * 100, 2),
            "risk_level": risk_level,
            "model": "Balanced Random Forest"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )