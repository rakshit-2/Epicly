import sys
import signal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import settings
from api import router as api_router
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

app.include_router(api_router) # APis from here

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
