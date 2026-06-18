from pydantic import BaseModel, Field
from typing import List, Optional


class CourseRecord(BaseModel):
    course_id: str
    grade: str
    credits: int = 3


class SemesterRecord(BaseModel):
    term_name: str = Field(..., example="2023 Fall")
    courses: List[CourseRecord]
    term_gpa: Optional[float] = None
    earned_credits: int = 0
    attempted_credits: int = 0
    cumulative_gpa: Optional[float] = None


class PredictRequest(BaseModel):
    student_id: str
    program: str = "Computer Science"
    school: str = "Engineering"
    entry_year: int = 2020
    semesters: List[SemesterRecord] = Field(
        ..., description="Completed semesters in chronological order"
    )


class PredictResponse(BaseModel):
    student_id: str
    predicted_gpa: float
    risk_level: str
    risk_probabilities: dict
    trajectory: str
    reasoning: dict
