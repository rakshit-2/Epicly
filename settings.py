import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
        
        self.is_production = self.ENVIRONMENT == "production"
        self.is_development = self.ENVIRONMENT == "development"
        
        env_prefix = "PROD_" if self.is_production else "DEV_"
        
        if self.is_production:
            self.DB_HOST = os.getenv("PROD_RDS_ENDPOINT", "")
            self.DB_PORT = int(os.getenv("PROD_RDS_PORT", 5432))
            self.DB_NAME = os.getenv("PROD_RDS_DB_NAME", "epicly_db")
            self.DB_USER = os.getenv("PROD_RDS_USERNAME", "postgres")
            self.DB_PASSWORD = os.getenv("PROD_RDS_PASSWORD", "postgres")
            self.DB_SSL_MODE = os.getenv("PROD_DB_SSL_MODE", "require")
            self.DB_SSL_CERT = os.getenv("PROD_DB_SSL_CERT", "")
        else:
            self.DB_HOST = os.getenv("DEV_DB_HOST", "localhost")
            self.DB_PORT = int(os.getenv("DEV_DB_PORT", 5432))
            self.DB_NAME = os.getenv("DEV_DB_NAME", "epicly_db")
            self.DB_USER = os.getenv("DEV_DB_USER", "postgres")
            self.DB_PASSWORD = os.getenv("DEV_DB_PASSWORD", "password")
            self.DB_SSL_MODE = None
            self.DB_SSL_CERT = None
        
        self.SERVER_HOST = os.getenv(f"{env_prefix}SERVER_HOST", "localhost" if self.is_development else "0.0.0.0")
        self.SERVER_PORT = int(os.getenv(f"{env_prefix}SERVER_PORT", 8000))
        
        self.SECRET_KEY = os.getenv(f"{env_prefix}SECRET_KEY", "dev-secret-key" if self.is_development else "")
        allowed_hosts_str = os.getenv(f"{env_prefix}ALLOWED_HOSTS", "localhost,127.0.0.1" if self.is_development else "*")
        self.ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(",")]
        
        self.DEBUG = os.getenv(f"{env_prefix}DEBUG", "true" if self.is_development else "false").lower() == "true"
        self.LOG_LEVEL = os.getenv(f"{env_prefix}LOG_LEVEL", "DEBUG" if self.is_development else "INFO")
        
        self.AWS_REGION = os.getenv("AWS_REGION", "us-east-1") if self.is_production else None
        
    def get_database_url(self) -> str:
        if self.is_production:
            url = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            if self.DB_SSL_MODE:
                url += f"?sslmode={self.DB_SSL_MODE}"
            return url
        else:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def __repr__(self):
        return f"Settings(environment={self.ENVIRONMENT}, debug={self.DEBUG})"


settings = Settings()
