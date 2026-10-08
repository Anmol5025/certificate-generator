from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from . import models, schemas, database, generator
import os

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Bulk Certificate Generator")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/jobs", response_model=schemas.JobResponse, status_code=202)
def create_job(job_req: schemas.JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not job_req.recipients:
        raise HTTPException(status_code=400, detail="Recipients list cannot be empty")
        
    db_job = models.Job(status="pending")
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    SessionClass = type(db)
    new_db = SessionClass(bind=db.get_bind())
    background_tasks.add_task(run_generator, db_job.id, job_req.recipients, new_db)
    
    return db_job

def run_generator(job_id, recipients, db_session):
    try:
        generator.generate_certificates(job_id, recipients, db_session)
    finally:
        db_session.close()

@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/certificates/{cert_id}/download")
def download_certificate(cert_id: int, db: Session = Depends(get_db)):
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if cert.status != "success" or not cert.file_path:
        raise HTTPException(status_code=400, detail="Certificate not generated successfully")
        
    if not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found on server")
        
    return FileResponse(path=cert.file_path, filename=os.path.basename(cert.file_path), media_type='image/png')
