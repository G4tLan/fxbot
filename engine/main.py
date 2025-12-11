import sys
import os

# Add parent dir to path so 'engine' package can be resolved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from engine.controllers import (
    import_controller, 
    backtest_controller, 
    websocket_controller, 
    lsp_controller, 
    config_controller,
    auth_controller,
    exchange_controller,
    task_controller
)
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
app.include_router(lsp_controller.router, prefix="/api/v1", tags=["LSP"])
app.include_router(config_controller.router, prefix="/api/v1", tags=["Config"])
app.include_router(auth_controller.router, prefix="/api/v1", tags=["Auth"])
app.include_router(exchange_controller.router, prefix="/api/v1", tags=["Exchange"])
app.include_router(task_controller.router, prefix="/api/v1", tags=["Tasks"])
app.include_router(websocket_controller.router, tags=["WebSocket"])

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"status": "online", "message": "FXBot Engine is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("engine.main:app", host="0.0.0.0", port=8000, reload=True)
