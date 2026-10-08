from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")  # pending, processing, completed
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    certificates = relationship("Certificate", back_populates="job")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    name = Column(String, index=True)
    email = Column(String)
    course = Column(String)
    status = Column(String, default="pending")  # pending, success, failed
    file_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)

    job = relationship("Job", back_populates="certificates")
