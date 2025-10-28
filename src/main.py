import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from src.api import router
from src.database import Base, engine, SessionLocal
from src.tasks.service import seed_default_task_icons
from src.file_upload.service import seed_preloaded_files
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Seed default task icons
try:
    db = SessionLocal()
    seed_default_task_icons(db)
    seed_preloaded_files(db)
    db.close()
except Exception as e:
    logger.error(f"Failed to seed default data: {str(e)}")

app = FastAPI(
    title="Calendar API",
    description="A comprehensive API for managing calendar events, family members, and home essentials",
    version="1.0.0"
)

# Mount /uploads for static file serving
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ============ GLOBAL EXCEPTION HANDLERS ============

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException with standardized response format"""
    logger.warning(f"HTTPException: {exc.status_code} - {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={ 
            "statusCode": exc.status_code, 
            "status": False, 
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "data": None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors (like missing headers) with standardized format"""
    error_details = []
    for error in exc.errors():
        if error["type"] == "missing":
            field_name = " -> ".join(str(loc) for loc in error["loc"])
            error_details.append(f"{field_name} is required")
        else:
            error_details.append(f"{error['loc'][-1]}: {error['msg']}")

    error_message = "; ".join(error_details)
    logger.warning(f"Validation Error: {error_message} - Path: {request.url.path}")

    return JSONResponse(
        status_code=422,
        content={
            "statusCode": 422,
            "status": False,
            "message": f"Validation Error: {error_message}",
            "data": None
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)} - Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "statusCode": 500,
            "status": False,
            "message": "Internal server error. Please try again later.",
            "data": None
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if(Data == Mansik){
#     vo sala chutya he
# }

# Include router
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the API. The server is operational."}
# if __name__ == "__main__":
#     uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
