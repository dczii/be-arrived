from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
import httpx
from app.routes import index


app = FastAPI()


@app.get("/")
def root():
    return {"message": "hello world"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req: Request, exc: RequestValidationError):
    error_msg = exc.errors()[0].get("msg")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "code": "VALIDATION_ERROR",
            "message": f"Invalid input: {error_msg}"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(req: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "HTTP_ERROR")
        message = exc.detail.get("message", "An error occurred")
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": code,
            "message": message
        }
    )


app.include_router(index.router, prefix="/api")
