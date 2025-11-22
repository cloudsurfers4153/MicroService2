import logging
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from google.cloud.sql.connector import Connector

from config import config
from models.db_models import Base

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None
connector = None


def get_connection():
    global connector
    if connector is None:
        connector = Connector()
    
    conn = connector.connect(
        config.CLOUD_SQL_CONNECTION_NAME,
        "pymysql",
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        db=config.DB_NAME
    )
    return conn


def init_database():
    global engine, SessionLocal
    
    if config.USE_CLOUD_SQL_CONNECTOR:
        logger.info(f"Connecting to Cloud SQL: {config.CLOUD_SQL_CONNECTION_NAME}")
        engine = create_engine(
            "mysql+pymysql://",
            creator=get_connection,
            poolclass=NullPool,
        )
    else:
        database_url = config.get_database_url()
        logger.info(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else database_url}")
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine and session factory initialized")


def init_db():
    if engine is None:
        init_database()
    
    logger.info("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        init_database()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_database():
    global connector, engine
    
    if connector is not None:
        connector.close()
        logger.info("Cloud SQL connector closed")
    
    if engine is not None:
        engine.dispose()
        logger.info("Database engine disposed")

