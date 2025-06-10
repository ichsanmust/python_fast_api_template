from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.controllers.module import UploadDataController
from app.core import config, database, security

from fastapi.responses import FileResponse
import pandas as pd
from datetime import datetime, timedelta

import shutil
import os
from app.models.module.Job import Job
import threading
import uuid
import random
from app.schemas.module import UploadDataSchema
from app.models.module.UploadData import UploadData


router = APIRouter()


@router.get("/template-excel")
def module_upload_data_download_template_excel(record: int = 10):
    # data = [
    #     {"nama": "Budi Santoso", "alamat": "Jl. Merdeka No. 1",
    #         "umur": 32, "tanggal_lahir": "1992-05-10"},
    #     {"nama": "Ani Wijaya", "alamat": "Jl. Kenanga No. 5",
    #         "umur": 28, "tanggal_lahir": "1996-08-23"},
    #     {"nama": "Dedi Prasetyo", "alamat": "Jl. Melati No. 17",
    #         "umur": 45, "tanggal_lahir": "1979-11-12"},
    # ]

    n = record

    # Data generator
    data = []
    for i in range(n):
        nama = f"User {i+1}"
        alamat = f"Alamat No. {i+1}"
        umur = random.randint(18, 65)
        tanggal_lahir = datetime(1960, 1, 1) + \
            timedelta(days=random.randint(0, 20000))

        data.append({
            "nama": nama,
            "alamat": alamat,
            "umur": umur,
            "tanggal_lahir": tanggal_lahir.strftime("%Y-%m-%d")
        })

    # Simpan ke file Excel
    df = pd.DataFrame(data)

    # Buat nama file unik sementara
    filename = f"template_excel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join("/tmp", filename)
    df.to_excel(filepath, index=False)

    # Kirim file langsung ke client sebagai download
    return FileResponse(
        path=filepath,
        filename=f"template_upload_{n}_records.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/upload-excel")
def module_upload_data_upload_excel(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join("/tmp", filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job = Job(filename=filename)
    db.add(job)
    db.commit()
    db.refresh(job)

    threading.Thread(target=UploadDataController.import_excel_worker, args=(
        job.id, filepath)).start()

    return {"message": "Upload received", "job_id": job.id}


@router.get("/upload-progress/{job_id}")
def module_upload_data_check_progress(job_id: int, db: Session = Depends(database.get_db)):
    job = db.query(Job).get(job_id)
    if not job:
        return {"status": "not_found", "progress": 0}

    progress = 0
    if job.total_rows > 0:
        progress = int((job.processed_rows / job.total_rows) * 100)

    return {
        "status": job.status,
        "progress": progress,
        "processed": job.processed_rows,
        "total": job.total_rows,
        "error": job.error
    }


@router.post("/upload-data", response_model=UploadDataSchema.Paginated, description="Get Data UP=ploaded Data with dynamic filter and sorting")
def master_data_user_read_all_search_dynamic(
    params: UploadDataSchema.SearchRequest,
    db: Session = Depends(database.get_db)
):
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
   
    # return {
    #     "upload_data": uploadData,
    #     "total": total,
    #     "page": params.page,
    #     "per_page": params.per_page
    # }

    responseUploadData = [UploadDataSchema.Out.from_orm(user) for user in uploadData]
    responseData = {
        "upload_data": responseUploadData,
        "total": total,
        "page": params.page,
        "per_page": params.per_page
    }

    return config.response_format(200, "success", "success get data", responseData)
