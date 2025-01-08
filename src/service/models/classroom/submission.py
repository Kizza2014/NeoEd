from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Submission(BaseModel):
    student_id: str
    submitted_at: datetime
    grade: Optional[float] = None
    attachments: Optional[List[dict]] = None

class Resubmission(BaseModel):
    student_id: str
    submitted_at: datetime = None
    additional_attachments: List[dict] = None
    removal_attachments: List[dict] = None
