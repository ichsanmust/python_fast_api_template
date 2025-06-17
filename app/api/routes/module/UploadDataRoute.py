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
from app.schemas.module import UploadDataSchema, JobSchema
from app.models.module.UploadData import UploadData
from fastapi import Query


router = APIRouter()


@router.get("/template-excel", description="Download Template excel", responses={
    200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            },
            "description": "Excel file generated successfully.",
            },
    422: {
        "model": config.ValidationErrorResponseModel,
        "description": "Validation error"
    },
    400: {
        "model": config.BadRequestResponseModel,
        "description": "Bad request"
    }
})
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


@router.post("/upload-excel", description="Upload Excel Based on Template excel", response_model=config.SingleDataResponseModel[JobSchema.Out],
             responses={
    422: {
        "model": config.ValidationErrorResponseModel,
        "description": "Validation error"
    },
    400: {
        "model": config.BadRequestResponseModel,
        "description": "Bad request"
    }
})
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

    responseData = {"message": "Upload received", "job_id": job.id}
    return config.response_format(200, "success", "success Upload", responseData)


@router.get("/upload-progress", description="Check Progress Upload Data excel", response_model=config.SingleDataResponseModel[JobSchema.OutProgress],
            responses={
    422: {
        "model": config.ValidationErrorResponseModel,
        "description": "Validation error"
    },
    400: {
        "model": config.BadRequestResponseModel,
        "description": "Bad request"
    }
})
def module_upload_data_check_progress(job_id: int = Query(...), db: Session = Depends(database.get_db)):
    job = db.query(Job).get(job_id)
    if not job:
        return {"status": "not_found", "progress": 0}

    progress = 0
    if job.total_rows > 0:
        progress = int((job.processed_rows / job.total_rows) * 100)

    processing_time_string = ''
    processing_time_in_second = 0
    if job.status in ['completed', 'failed']:
        processing_time = UploadDataController.get_rocessing_time(
            job.created_at, job.updated_at)
        processing_time_string = processing_time['format_dinamis']
        processing_time_in_second = processing_time['selisih_detik']

    responseData = {
        "status": job.status,
        "processing_message": job.processing_message,
        "progress": progress,
        "processed": job.processed_rows,
        "total": job.total_rows,
        "error": job.error,
        "processing_time_string": processing_time_string,
        "processing_time_second": processing_time_in_second
    }

    return config.response_format(200, "success", "success get progress data", responseData)


@router.post("/upload-data", response_model=config.SingleDataResponseModel[UploadDataSchema.Paginated],
             responses={
    422: {
        "model": config.ValidationErrorResponseModel,
        "description": "Validation error"
    },
    400: {
        "model": config.BadRequestResponseModel,
        "description": "Bad request"
    }
}, description="""
    Get Data Uploaded Data with dynamic filter and sorting
    <br>
    #example Body Format:
    <br>
    - `"filters": {"nama": "user", "alamat": "alamat"},`
    <br>
    - `"sorting": {"nama": "desc", "alamat": "asc"},`
    """)
def module_upload_data_read_data_search_post(
    params: UploadDataSchema.SearchRequest,
    db: Session = Depends(database.get_db)
):
    getData = UploadDataController.get_data(params, db)
    responseUploadData = [UploadDataSchema.Out.from_orm(
        user) for user in getData['uploadData']]
    responseData = {
        "upload_data": responseUploadData,
        "total": getData['total'],
        "page": params.page,
        "per_page": params.per_page
    }

    return config.response_format(200, "success", "success get data", responseData)
