from pydantic import BaseModel
from typing import Dict, List, Optional


class TranscriptSummary(BaseModel):
    semester_gpas: List[float]
    cumulative_gpa: float
    total_credits_completed: int
    total_credits_attempted: int
    fail_withdrawal_count: int
    domain_gpas: Dict[str, float]
    academic_standing: Optional[str] = None


class StudentRequest(BaseModel):
    student_id: str
    program: Optional[str] = None
    transcript_summary: TranscriptSummary


class Predictions(BaseModel):
    next_semester_gpa: float
    predicted_graduation_gpa: float
    trajectory: str
    risk_level: str
    risk_score: float


class StudentResponse(BaseModel):
    student_id: str
    predictions: Predictions
    alerts: List[str]
    recommendations: List[str]
