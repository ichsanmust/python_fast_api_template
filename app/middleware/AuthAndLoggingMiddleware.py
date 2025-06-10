from fastapi import Request
from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from jose import JWTError, jwt, ExpiredSignatureError
import time
import os
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.core import config, security
from app.models.log.RequestLog import RequestLog
import json
from datetime import datetime
from starlette.types import Message


def sanitize_sensitive_fields(body_str: str) -> str:
    try:
        data = json.loads(body_str)
        if isinstance(data, dict):
            for key in data:
                if any(word in key.lower() for word in ["password", "pass", "pwd"]):
                    data[key] = "***"
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        # Return original if not JSON (e.g., plain text or invalid JSON)
        return body_str


class AuthAndLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db_gen = get_db()
        db: Session = next(db_gen)
        user_id = 0
        request_body = ""
        response_body = ""
        start_time = time.time()

        try:
            # Read and cache request body
            request_body_bytes = await request.body()
            # request_body = request_body_bytes.decode("utf-8")
            try:
                request_body = request_body_bytes.decode("utf-8")
            except UnicodeDecodeError:
                request_body = "<binary request body>"

            async def receive() -> Message:
                return {
                    "type": "http.request",
                    "body": request_body_bytes,
                    "more_body": False,
                }
            request = Request(request.scope, receive)
            method = request.method.upper()
            path = request.url.path

            if config.is_excluded(method, path):
                response = await call_next(request)
            else:

                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    return config.response_format(status.HTTP_401_UNAUTHORIZED, "failed", "Unauthorized", {"Authenticate": "No Bearer"})

                token = auth_header.split(" ")[1]

                payload = security.verify_token(token)

                # error berier
                if not hasattr(payload, "get"):
                    return payload

                request.state.user = payload
                user_id = payload.get("user_id")

                # Intercept the response and read the body
                response = await call_next(request)

            # Read response body
            response_body_bytes = b""
            async for chunk in response.body_iterator:
                response_body_bytes += chunk

            # response_body = response_body_bytes.decode("utf-8")
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type or "text" in content_type:
                try:
                    response_body = response_body_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    response_body = "<invalid utf-8 response>"
            else:
                response_body = "<binary response not logged>"

            # Create a new response with the same body
            new_response = Response(
                content=response_body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )

            # Logging
            process_time = time.time() - start_time
            if new_response.status_code != 307:
                sanitized_body = sanitize_sensitive_fields(request_body)
                try:
                    sanitized_json = json.loads(sanitized_body)
                except Exception:
                    sanitized_json = sanitized_body  # fallback to string if not JSON

                # Attempt to parse response body as JSON
                try:
                    response_json = json.loads(response_body)
                except Exception:
                    response_json = response_body  # fallback to string if not JSON

                short_sanitized_json = json.dumps(
                    sanitized_json,
                    ensure_ascii=False)

                short_response_json = json.dumps(
                    response_json,
                    ensure_ascii=False)

                log = RequestLog(
                    user_id=user_id,
                    method=request.method,
                    path=request.url.path,
                    status_code=str(new_response.status_code),
                    process_time=round(process_time, 4),
                    timestamp=datetime.now(config.TIMEZONE),
                    request=short_sanitized_json[:10000],
                    response=short_response_json[:10000],
                )
                db.add(log)
                db.commit()

            new_response.headers['X-Content-Type-Options'] = "nosniff"
            new_response.headers['X-Frame-Options'] = "DENY"
            new_response.headers['X-XSS-Protection'] = "1; mode=block"
            return new_response

        finally:
            db_gen.close()
