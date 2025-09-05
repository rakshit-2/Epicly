import sys
import signal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import settings
from contextlib import asynccontextmanager
from database import test_connection, create_tables, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    if test_connection():
        if settings.is_development:
            create_tables()
    else:
        if settings.is_production:
            raise Exception("Database connection failed in production")
    
    yield
    engine.dispose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS if settings.ALLOWED_HOSTS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def signal_handler(signum, frame):
    engine.dispose()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": f"Epicly Event Booking System - {settings.ENVIRONMENT.title()}",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "debug": settings.DEBUG
    }

@app.get("/config")
async def get_config():
    if settings.is_production:
        return {"error": "Configuration endpoint not available in production"}
    
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database": {
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "name": settings.DB_NAME,
            "user": settings.DB_USER
        },
        "server": {
            "host": settings.SERVER_HOST,
            "port": settings.SERVER_PORT
        },
        "log_level": settings.LOG_LEVEL
    }




if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG,
        reload=settings.DEBUG
    )
