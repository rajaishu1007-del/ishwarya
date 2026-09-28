from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routes import router

app = FastAPI(title="Comic Craft AI")

# Static files
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Routes
app.include_router(router)