import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "db")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    
    CLOUD_SQL_CONNECTION_NAME: str = os.getenv(
        "CLOUD_SQL_CONNECTION_NAME",
        "coms4153-cloud-surfers:us-central1:microservice2-movie-db"
    )
    
    USE_CLOUD_SQL_CONNECTOR: bool = os.getenv("USE_CLOUD_SQL_CONNECTOR", "false").lower() == "true"
    
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    
    @classmethod
    def get_database_url(cls) -> Optional[str]:
        if not cls.USE_CLOUD_SQL_CONNECTOR:
            return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        return None


config = Config()

