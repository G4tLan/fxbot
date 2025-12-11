import sys
import os

# Add parent dir to path so 'engine' package can be resolved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from engine.controllers import import_controller, backtest_controller
from engine.init_db import init_db

app = FastAPI(title="FXBot Engine API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(import_controller.router, prefix="/api/v1", tags=["Import"])
app.include_router(backtest_controller.router, prefix="/api/v1", tags=["Backtest"])

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"status": "online", "message": "FXBot Engine is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("engine.main:app", host="0.0.0.0", port=8000, reload=True)
