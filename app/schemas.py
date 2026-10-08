from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
import datetime

class Recipient(BaseModel):
    name: str
    email: EmailStr
    course: str

class JobCreate(BaseModel):
    recipients: List[Recipient]

class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    course: str
    status: str
    file_path: Optional[str] = None
    error_message: Optional[str] = None

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    created_at: datetime.datetime
    certificates: List[CertificateResponse] = []
