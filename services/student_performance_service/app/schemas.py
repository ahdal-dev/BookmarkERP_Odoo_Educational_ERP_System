from pydantic import BaseModel, Field
from typing import List, Optional


class CourseRecord(BaseModel):
    course_id: str
    grade: str
    credits: int = 3
    title: str = ""
    subtype: str = "LECTURE"


class SemesterRecord(BaseModel):
    term_name: str = Field(..., example="2023 Fall")
    courses: List[CourseRecord]
    term_gpa: Optional[float] = None
    earned_credits: int = 0
    attempted_credits: int = 0
    cumulative_gpa: Optional[float] = None


class PlannedCourse(BaseModel):
    course_id: str
    credits: int = 3
    title: str = ""
    subtype: str = "LECTURE"


class PredictRequest(BaseModel):
    student_id: str
    program: str = "Computer Science"
    school: str = "Engineering"
    entry_year: int = 2020
    semesters: List[SemesterRecord] = Field(
        ..., description="Completed semesters in chronological order"
    )
    study_plan: List[PlannedCourse] = Field(
        ..., description="Courses planned for the NEXT semester (no grades — these are the target)"
    )


class PredictResponse(BaseModel):
    student_id: str
    predicted_gpa: float
    interval_lo: float
    interval_hi: float
    at_risk_probability: float
    at_risk: bool
    trajectory: str
    graduation_gpa_estimate: float
    reasoning: dict
