from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CriterionScore(BaseModel):
    name: str
    description: str
    score: float
    weight: float
    grade: str


class PoseFeedbackRequest(BaseModel):
    exercise_type: str  # squat, bench_press, deadlift
    total_score: int
    criteria_scores: List[CriterionScore]
    detected_issues: List[str]


class PoseFeedbackResponse(BaseModel):
    success: bool
    feedback: str
    session_id: Optional[int] = None


class PoseHistoryItem(BaseModel):
    id: int
    exercise_type: str
    total_score: int
    feedback_text: Optional[str]
    created_at: datetime


class PoseHistoryResponse(BaseModel):
    success: bool
    history: List[PoseHistoryItem]
