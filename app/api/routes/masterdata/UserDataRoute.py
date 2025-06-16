from fastapi import APIRouter, Body, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.schemas.masterdata import UserDataSchema
from app.controllers.masterdata import UserDataController
from app.core import config, database, security

from sqlalchemy import or_
from typing import Optional
from datetime import datetime

from app.models.masterdata.UserData import UserData


router = APIRouter()


@router.get("/users", description="Master Data User Read All Standard", response_model=config.MultiDataResponseModel[list[UserDataSchema.Out]],
            responses={
    422: {
            "model": config.ValidationErrorResponseModel,
            },
    400: {
        "model": config.BadRequestResponseModel,
    }
})
def master_data_user_read_all(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    data = UserDataController.findAll(db, skip, limit)

    response = [UserDataSchema.Out.from_orm(user) for user in data]
    return config.response_format(200, "success", "success get data", response)


@router.post("/users", description="Create Data User", response_model=config.SingleDataResponseModel[UserDataSchema.Out],
             responses={
    422: {
        "model": config.ValidationErrorResponseModel,
    },
    400: {
        "model": config.BadRequestResponseModel,
    }
})
def master_data_user_create(user: UserDataSchema.Create, db: Session = Depends(database.get_db), user_login: dict = Depends(security.get_current_user)):
    if UserDataController.findByAttribute(db, 'username', user.username):
        raise HTTPException(
            status_code=400, detail=f"Username '{user.username}' already exists")
    if UserDataController.findByAttribute(db, 'email', user.email):
        raise HTTPException(
            status_code=400, detail=f"Email '{user.email}' already exists")

    user_id = user_login.get("user_id")
    inserted = UserDataController.create(db, user, user_id)
    response = UserDataSchema.Out.from_orm(inserted)
    return config.response_format(200, "success", "success insert data", response)


@router.get("/users-search", response_model=config.SingleDataResponseModel[UserDataSchema.Paginated], responses={
    422: {
        "model": config.ValidationErrorResponseModel,
    },
    400: {
        "model": config.BadRequestResponseModel,
    }
},
    description="Master Data User Read All with Search (like username or like email)")
def master_data_user_read_all_search(
    request: Request,
    db: Session = Depends(database.get_db),
    search: str = Query(
        default="",
        title="Search",
        description="Filter user data by username or email",
        example="admin"
    ),
    # start_date: Optional[datetime] = None,
    # end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    query = db.query(UserData)

    # --- Dynamic filters from filter[...]
    # for key, value in request.query_params.items():
    #     if key.startswith("filter[") and key.endswith("]"):
    #         field_name = key[7:-1]
    #         if hasattr(UserData, field_name):
    #             col = getattr(UserData, field_name)
    #             if value.isdigit():
    #                 query = query.filter(col == int(value))
    #             else:
    #                 query = query.filter(col.like(f"%{value}%"))

    # --- Global search
    search = request.query_params.get("search")
    if search:
        query = query.filter(
            or_(
                UserData.username.like(f"%{search}%"),
                UserData.email.like(f"%{search}%")
            )
        )

    # --- Date filter
    # if "start_date" in request.query_params:
    #     start_date = datetime.fromisoformat(request.query_params["start_date"])
    #     query = query.filter(UserData.created_date >= start_date)
    # if "end_date" in request.query_params:
    #     end_date = datetime.fromisoformat(request.query_params["end_date"])
    #     query = query.filter(UserData.created_date <= end_date)

    # --- Sorting from sorting[field]=asc|desc
    # sort_clauses = []
    # for key, value in request.query_params.items():
    #     if key.startswith("sorting[") and key.endswith("]"):
    #         field_name = key[8:-1]
    #         if hasattr(UserData, field_name):
    #             col = getattr(UserData, field_name)
    #             sort_clauses.append(
    #                 col.desc() if value.lower() == "desc" else col.asc())

    # if sort_clauses:
    #     query = query.order_by(*sort_clauses)

    # --- Pagination
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", 10))
    offset = (page - 1) * per_page
    total = query.count()
    getData = query.offset(offset).limit(per_page).all()

    # return {
    #     "user_data": users,
    #     "total": total,
    #     "page": page,
    #     "per_page": per_page
    # }

    responseUploadData = [UserDataSchema.Out.from_orm(
        user) for user in getData]
    responseData = {
        "user_data": responseUploadData,
        "total": total,
        "page": page,
        "per_page": per_page
    }
    return config.response_format(200, "success", "success get data", responseData)


@router.post("/users-search", response_model=config.SingleDataResponseModel[UserDataSchema.Paginated], responses={
    422: {
        "model": config.ValidationErrorResponseModel,
    },
    400: {
        "model": config.BadRequestResponseModel,
    }
},
    description="""
    Master Data User Read All with dynamic filter and sorting
    <br>
    #example Body Format:
    <br>
    - `"filters": {"username": "admin", "active": "1"},`
    <br>
    - `"sorting": {"created_date": "desc", "username": "asc"},`
    """)
def master_data_user_read_all_search_dynamic(
    params: UserDataSchema.SearchRequest = Body(
        example={
            "filters": {
                "username": "john",
                "status": "active"
            },
            "sorting": {
                "created_date": "desc",
                "username": "asc"
            },
            "page": 3,
            "per_page": 30
        }
    ),
    db: Session = Depends(database.get_db)
):
    query = db.query(UserData)

    # FILTER dinamis
    if params.filters:
        for field, value in params.filters.items():
            if hasattr(UserData, field):
                col = getattr(UserData, field)
                if str(value).isdigit():
                    query = query.filter(col == int(value))
                else:
                    query = query.filter(col.like(f"%{value}%"))

    # SEARCH global
    # if params.search:
    #     query = query.filter(
    #         or_(
    #             UserData.username.like(f"%{params.search}%"),
    #             UserData.email.like(f"%{params.search}%")
    #         )
    #     )

    # FILTER tanggal
    # if params.start_date:
    #     query = query.filter(UserData.created_date >= params.start_date)

    # if params.end_date:
    #     query = query.filter(UserData.created_date <= params.end_date)

    # SORTING dinamis
    if params.sorting:
        sort_clauses = []
        for field, direction in params.sorting.items():
            if hasattr(UserData, field):
                col = getattr(UserData, field)
                sort_clauses.append(
                    col.desc() if direction.lower() == "desc" else col.asc())
        if sort_clauses:
            query = query.order_by(*sort_clauses)

    # PAGINATION
    offset = (params.page - 1) * params.per_page
    total = query.count()
    getData = query.offset(offset).limit(params.per_page).all()

    # return {
    #     "user_data": users,
    #     "total": total,
    #     "page": params.page,
    #     "per_page": params.per_page
    # }

    responseUploadData = [UserDataSchema.Out.from_orm(
        user) for user in getData]
    responseData = {
        "user_data": responseUploadData,
        "total": total,
        "page": params.page,
        "per_page": params.per_page
    }

    return config.response_format(200, "success", "success get data", responseData)


@router.get("/users/{user_id}", response_model=config.SingleDataResponseModel[UserDataSchema.Out],
            responses={
    422: {
            "model": config.ValidationErrorResponseModel,
            },
    400: {
        "model": config.BadRequestResponseModel,
    }
},
    description="Get Data User by ID")
def master_data_user_read_one(user_id: int, db: Session = Depends(database.get_db)):
    data = UserDataController.findByPK(db, user_id)
    if not data:
        raise HTTPException(
            status_code=400, detail="Data Not Found")

    response = UserDataSchema.Out.from_orm(data)
    return config.response_format(200, "success", "success get data", response)


@router.put("/users/{user_id}", response_model=config.SingleDataResponseModel[UserDataSchema.Out],
            responses={
    422: {
            "model": config.ValidationErrorResponseModel,
            },
    400: {
        "model": config.BadRequestResponseModel,
    }
},
    description="Update Data User by ID")
def master_data_user_update(user_id: int, user: UserDataSchema.Update, db: Session = Depends(database.get_db), user_login: dict = Depends(security.get_current_user)):
    data = UserDataController.findByPK(db, user_id)

    if not data:
        raise HTTPException(
            status_code=400, detail="Data Not Found")
    if UserDataController.findByAttributeOnUpdate(db, 'username', user.username, data.id):
        raise HTTPException(
            status_code=400, detail=f"Username '{user.username}' already exists")
    if UserDataController.findByAttributeOnUpdate(db, 'email', user.email, data.id):
        raise HTTPException(
            status_code=400, detail=f"Email '{user.email}' already exists")

    user_id = user_login.get("user_id")
    updated = UserDataController.update(db, data, user, user_id)

    response = UserDataSchema.Out.from_orm(updated)
    return config.response_format(200, "success", "success update data", response)


@router.delete("/users/{user_id}", response_model=config.SingleDataResponseModel[UserDataSchema.OutDeleted],
               responses={
    422: {
        "model": config.ValidationErrorResponseModel,
    },
    400: {
        "model": config.BadRequestResponseModel,
    }
},
    description="Delete Data User by ID")
def master_data_user_delete(user_id: int, db: Session = Depends(database.get_db)):
    data = UserDataController.findByPK(db, user_id)
    if not data:
        raise HTTPException(
            status_code=400, detail="Data Not Found")

    delete = UserDataController.delete(db, data)
    data = {
        "message": f"User '{data.id}' has been deleted"
    }
    return config.response_format(200, "success", 'success delete data', data)
