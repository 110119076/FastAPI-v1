from pydantic import BaseModel, Field
from typing import Dict

class PredictionResponse(BaseModel):
    predicted_category: str = Field(..., description="The predicted insurance category", example="High")
    confidence: float = Field(..., description="The confidence score of the prediction", example=0.85)
    class_probabilities: Dict[str, float] = Field(..., description="A dictionary containing the probabilities for each class", example={"Low": 0.1, "Medium": 0.05, "High": 0.85})