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


def get_data(params, db):
    query = db.query(UploadData)

    # FILTER dinamis
    # if params.filters:
    #     for field, value in params.filters.items():
    #         if hasattr(UploadData, field):
    #             col = getattr(UploadData, field)
    #             if str(value).isdigit():
    #                 query = query.filter(col == int(value))
    #             else:
    #                 query = query.filter(col.like(f"%{value}%"))

    # if params.filters:
    #     for field, value in params.filters.items():
    #         if hasattr(UploadData, field):
    #             col = getattr(UploadData, field)
    #             if str(col.type).__contains__('INTEGER'):
    #                 query = query.filter(col == int(value))
    #             else:
    #                 query = query.filter(col.like(f"%{value}%"))

    if params.filters:
        for field, value in params.filters.items():
            if hasattr(UploadData, field):
                col = getattr(UploadData, field)
                query = query.filter(col.like(f"%{value}%"))

    # SORTING dinamis
    if params.sorting:
        sort_clauses = []
        for field, direction in params.sorting.items():
            if hasattr(UploadData, field):
                col = getattr(UploadData, field)
                sort_clauses.append(
                    col.desc() if direction.lower() == "desc" else col.asc())
        if sort_clauses:
            query = query.order_by(*sort_clauses)

    # PAGINATION
    offset = (params.page - 1) * params.per_page
    total = query.count()
    uploadData = query.offset(offset).limit(params.per_page).all()

    return {
        "total": total,
        "uploadData": uploadData
    }
