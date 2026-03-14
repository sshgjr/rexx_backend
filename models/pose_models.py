from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


class PoseEvaluation(Base):
    __tablename__ = "pose_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_type = Column(String(20), nullable=False)  # squat, bench_press, deadlift
    total_score = Column(Integer, nullable=False)
    criteria_scores_json = Column(Text, nullable=False)
    detected_issues_json = Column(Text, nullable=False)
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
