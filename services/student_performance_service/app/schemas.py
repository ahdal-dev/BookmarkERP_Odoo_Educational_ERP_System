from pydantic import BaseModel
from typing import Dict, List


class TranscriptSummary(BaseModel):
    semester_gpas: List[float]
    cumulative_gpa: float
    total_credits_completed: int
    total_credits_attempted: int
    fail_withdrawal_count: int
    domain_gpas: Dict[str, float]


class StudentRequest(BaseModel):
    student_id: str
    transcript_summary: TranscriptSummary