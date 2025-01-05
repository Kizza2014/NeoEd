from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Submission(BaseModel):
    student_id: str
    submitted_at: datetime
    grade: Optional[float] = None
    attachments: Optional[List[str]] = None