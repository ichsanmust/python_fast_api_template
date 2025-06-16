from fastapi import FastAPI, Request

import logging
import traceback
from app.core.database import engine
from app.models.log.ErrorLog import error_logs
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from app.api.routes.auth import AuthRoute
from app.api.routes.masterdata import UserDataRoute
from app.api.routes.module import UploadDataRoute
from app.core import config
from fastapi.openapi.utils import get_openapi
from app.middleware.AuthAndLoggingMiddleware import AuthAndLoggingMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import compile_path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title=config.APPTITLE,
    version=config.APPVERSION,
    docs_url=None, redoc_url=None
)


# access rule, log
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=config.APPTITLE,
        version=config.APPVERSION,
        description=config.APPDESCRIPTION,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
    }

    # for path, methods in openapi_schema["paths"].items():
    #     for method, details in methods.items():
    #         if not config.is_excluded(method.upper(), path):
    #             details.setdefault("security", []).append(
    #                 {
    #                     "OAuth2PasswordBearer": []
    #                 }
    #             )

    for path, methods in openapi_schema["paths"].items():
        for method, details in methods.items():
            if not config.is_excluded(method.upper(), path):
                # pastikan field "security" ada
                security_list = details.setdefault("security", [])
                
                # cek apakah "OAuth2PasswordBearer" sudah ada
                already_exists = any("OAuth2PasswordBearer" in s for s in security_list)

                if not already_exists:
                    security_list.append({
                        "OAuth2PasswordBearer": []
                    })


    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.add_middleware(AuthAndLoggingMiddleware)

# Tambahkan CORS jika perlu test dari front-end lokal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# end access rule, log


# route
@app.get("/", tags=["index"], summary="Index", description="Index")
def read_root():
    return {"message": "Welcome to Python Fast Api"}


@app.get("/rapidoc", include_in_schema=False)
def custom_rapidoc():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>RapiDoc</title>
        <script type="module" src="/static/rapidoc/rapidoc-min.js"></script>
    </head>
    <body>
        <rapi-doc
        spec-url="/openapi.json"
        render-style="read"
        theme="light"
        show-header="true"
        heading-text="Dokumentasi Fast Api Python"
        font-size="large"
        regular-font="Open Sans"
        mono-font="Fira Code"
        allow-authentication="true"
        allow-try="true"
        persist-auth="true"
        show-components="false"
        show-info="true"
        default-schema-tab="example"
        show-method-in-nav-bar="as-colored-block"
        use-path-in-nav-bar="true"
        show-curl-before-try="true"
        />
        </rapi-doc>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(AuthRoute.router, prefix="/auth", tags=["authentication"])
app.include_router(UserDataRoute.router, prefix="/master", tags=["masterdata"])
app.include_router(UploadDataRoute.router, prefix="/module", tags=["module"])
# end route


@app.middleware("http")
async def check_route_middleware(request: Request, call_next):
    path = request.scope["path"]
    method = request.scope["method"]

    # ✅ Lewati pengecekan untuk file static (misal: /static/rapidoc/...)
    if path.startswith("/static/"):
        return await call_next(request)

    found = False
    method_allowed = False

    for route in app.router.routes:
        if not hasattr(route, "methods"):
            continue

        # Cocokkan path dengan path route (dukung path dinamis)
        path_regex, path_format, param_convertors = compile_path(route.path)
        match = path_regex.match(path)

        if match:
            found = True
            if method in route.methods:
                method_allowed = True
                break

    if not found:
        return config.response_format(
            404,
            "error",
            f"Route '{path}' not found",
            None
        )
        # return JSONResponse(
        #     status_code=404,
        #     content={
        #         "detail": f"Route '{path}' tidak ditemukan (custom middleware)"}
        # )

    if not method_allowed:
        return config.response_format(
            405,
            "error",
            f"Metode '{method}' not allowed for path {path}",
            None
        )
        # return JSONResponse(
        #     status_code=405,
        #     content={
        #         "detail": f"Metode '{method}' tidak diizinkan untuk path {path}"}
        # )

    return await call_next(request)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_id = None

    try:
        with engine.begin() as conn:
            result = conn.execute(
                error_logs.insert().values(
                    # message=str(exc),
                    message=traceback.format_exc(),
                    path=str(request.url.path),
                    created_date=datetime.now(config.TIMEZONE)
                )
            )
            log_id = result.inserted_primary_key[0]  # Ambil ID dari log
    except Exception as db_error:
        logging.error(f"Failed save error log into DB: {db_error}")

    # Susun pesan dengan Log ID jika tersedia
    user_message = "An unexpected system error has occurred. Please try again later."
    if log_id:
        user_message += f" (Log ID: #{log_id})"

    return config.response_format(500, "error", user_message, None)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    return config.response_format(422, "failed", "Failed Input Validation", errors)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return config.response_format(
        exc.status_code,
        "error",
        exc.detail,
        None
    )

    # if exc.status_code == 404 or exc.status_code == 405:
    #     return config.response_format(
    #         404,
    #         "failed",
    #         exc.detail,
    #         None
    #     )
    # # Untuk exception lainnya, bisa gunakan default bawaan atau kustom lain
    # return JSONResponse(
    #     status_code=exc.status_code,
    #     content={"detail": exc.detail},
    # )
