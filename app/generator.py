import os
import uuid
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session
from . import models
from .schemas import Recipient

def generate_certificates(job_id: int, recipients: list[Recipient], db: Session):
    # First, update job status to processing
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        return
    job.status = "processing"
    db.commit()

    template_path = "assets/template.png"
    
    # Check if template exists, otherwise create a simple one
    if not os.path.exists(template_path):
        os.makedirs("assets", exist_ok=True)
        img = Image.new('RGB', (800, 600), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([20, 20, 780, 580], outline=(0, 0, 0), width=5)
        img.save(template_path)

    os.makedirs("certs", exist_ok=True)

    try:
        font = ImageFont.load_default()
    except:
        font = None

    for recipient in recipients:
        cert_record = models.Certificate(
            job_id=job_id,
            name=recipient.name,
            email=recipient.email,
            course=recipient.course,
            status="processing"
        )
        db.add(cert_record)
        db.commit()
        db.refresh(cert_record)

        try:
            img = Image.open(template_path).copy()
            draw = ImageDraw.Draw(img)
            
            # Simple text placement
            draw.text((100, 200), f"Certificate of Completion", fill=(0, 0, 0), font=font)
            draw.text((100, 300), f"Name: {recipient.name}", fill=(0, 0, 0), font=font)
            draw.text((100, 350), f"Course: {recipient.course}", fill=(0, 0, 0), font=font)
            
            filename = f"cert_{cert_record.id}_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join("certs", filename)
            
            img.save(filepath)
            
            cert_record.status = "success"
            cert_record.file_path = filepath
        except Exception as e:
            cert_record.status = "failed"
            cert_record.error_message = str(e)
        
        db.commit()

    job.status = "completed"
    db.commit()
