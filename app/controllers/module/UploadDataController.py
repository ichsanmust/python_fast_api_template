import pandas as pd
from sqlalchemy.orm import Session
from app.models.module.UploadData import UploadData
from app.models.module.Job import Job
from app.core.database import Base, SessionLocal


def import_excel_worker(job_id: int, filepath: str):
    db: Session = SessionLocal()
    try:
        job = db.query(Job).get(job_id)
        job.status = "processing"
        db.commit()

        df = pd.read_excel(filepath)
        job.total_rows = len(df)
        db.commit()

        for i, row in df.iterrows():
            data = UploadData(
                nama=row['nama'],
                alamat=row['alamat'],
                umur=int(row['umur']),
                tanggal_lahir=pd.to_datetime(row['tanggal_lahir']),
            )
            db.add(data)
            db.commit()

            # update progress
            job.processed_rows = i + 1
            db.commit()

        job.status = "completed"
        db.commit()
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        db.commit()
    finally:
        db.close()
