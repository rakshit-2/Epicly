from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models import Base
from settings import settings

def create_database_engine():
    database_url = settings.get_database_url()
    engine_config = { "pool_pre_ping": True, "echo": settings.DEBUG }
    
    if settings.is_production:
        engine_config.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 3600,
        })
    else:
        engine_config.update({
            "poolclass": StaticPool,
        })
    
    return create_engine(database_url, **engine_config)

engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        return False

def drop_tables():
    try:
        Base.metadata.drop_all(bind=engine)
        return True
    except Exception as e:
        return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        return False

def get_database_info():
    return {
        "environment": settings.ENVIRONMENT,
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "database": settings.DB_NAME,
        "user": settings.DB_USER,
        "ssl_mode": getattr(settings, 'DB_SSL_MODE', None),
        "debug": settings.DEBUG
    }

if __name__ == "__main__":
    db_info = get_database_info()
    
    if test_connection():
        if create_tables():
            print("xoxo -> db done")
        else:
            print("xoxo -> db failed")
    else:
        print("xoxo -> test connection failed")
