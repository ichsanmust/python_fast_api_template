import pandas as pd
from sqlalchemy.orm import Session
from app.models.module.UploadData import UploadData
from app.models.module.Job import Job
from app.core.database import Base, SessionLocal
from sqlalchemy import insert

upload_table = UploadData.__table__


def insert_batch_raw(db, data):
    upload_table = UploadData.__table__  # Akses table dengan benar
    stmt = insert(upload_table)
    db.execute(stmt, data)
    db.commit()


# v1
# def import_excel_worker(job_id: int, filepath: str):
#     db: Session = SessionLocal()
#     try:
#         job = db.query(Job).get(job_id)
#         job.status = "processing"
#         job.processed_rows = 0
#         db.commit()

#         df = pd.read_excel(filepath)
#         job.total_rows = len(df)
#         db.commit()

#         batch_size = 1000
#         total_rows = len(df)

#         for start in range(0, total_rows, batch_size):
#             end = min(start + batch_size, total_rows)
#             batch_df = df.iloc[start:end]

#             # Ubah DataFrame ke list of dicts
#             mappings = []
#             for _, row in batch_df.iterrows():
#                 mappings.append({
#                     "nama": row["nama"],
#                     "alamat": row["alamat"],
#                     "umur": int(row["umur"]),
#                     "tanggal_lahir": pd.to_datetime(row["tanggal_lahir"]),
#                 })

#             # Bulk insert dan update progress
#             db.bulk_insert_mappings(UploadData, mappings)
#             job.processed_rows = end
#             db.commit()

#         job.status = "completed"
#         db.commit()
#     except Exception as e:
#         job.status = "failed"
#         job.error = str(e)
#         db.commit()
#     finally:
#         db.close()

# v2
def import_excel_worker(job_id: int, filepath: str):
    db: Session = SessionLocal()
    try:
        # Ambil job dari DB dan tandai sebagai "processing"
        job = db.query(Job).get(job_id)
        job.status = "processing"
        job.processed_rows = 0
        db.commit()

        # Baca file Excel
        df = pd.read_excel(filepath)
        total_rows = len(df)
        job.total_rows = total_rows
        db.commit()

        # Atur ukuran batch (bisa diubah sesuai kebutuhan)
        batch_size = 1000

        # Proses per batch
        for start in range(0, total_rows, batch_size):
            end = min(start + batch_size, total_rows)
            batch_df = df.iloc[start:end]

            # Konversi langsung ke list of dicts
            mappings = batch_df.to_dict(orient="records")

            # Format tanggal dan umur (bisa disesuaikan sesuai kebutuhan data)
            for row in mappings:
                # row["tanggal_lahir"] = pd.to_datetime(row["tanggal_lahir"]) #ini kalo di hide memangkas jauh lebih cepat, jadi bagusnya di excel nya sudah di set formatnya konsisten YYYY-MM-DD
                row["umur"] = int(row["umur"])

            # Bulk insert pakai SQLAlchemy Core
            insert_batch_raw(db, mappings)

            # Update progres
            job = db.query(Job).get(job_id)
            job.processed_rows = end
            db.commit()

        # Sukses
        job = db.query(Job).get(job_id)
        job.status = "completed"
        db.commit()

    except Exception as e:
        # Tangani error
        job = db.query(Job).get(job_id)
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
