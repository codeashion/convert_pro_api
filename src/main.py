import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import router
from src.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Contractor and CHI Management API",
    description="Contractor and CHI Management API",
    version="1.0.0"
)

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "status": False,
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
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
