from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api.convert.routes import router as convert_router
import os

app = FastAPI(
    title="ConvertPro API",
    version="1.0.0"
)

POPPLER_BIN = r"D:\poppler-25.12.0\Library\bin"

if POPPLER_BIN not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + POPPLER_BIN

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "storage", "outputs")

# ✅ Make outputs publicly accessible
app.mount(
    "/downloads",
    StaticFiles(directory=OUTPUT_DIR),
    name="downloads"
)


app.mount("/static", StaticFiles(directory="src/storage"), name="static")
app.mount("/storage", StaticFiles(directory="src/storage"), name="storage")

app.include_router(convert_router, prefix="/api/convert")

@app.get("/")
def root():
    return {"message": "ConvertPro API running"}
