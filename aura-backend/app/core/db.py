import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

# Default MySQL configuration provided by user
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "marte")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "db_madera_poltand")

MYSQL_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLITE_URL = "sqlite:///./aura_database.db"

# Determine DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", MYSQL_URL)

engine = None
SessionLocal = None

try:
    logger.info(f"Attempting connection to primary database ({DATABASE_URL.split('@')[-1]})...")
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    # Test connection
    with engine.connect() as conn:
        logger.info("Successfully connected to primary MySQL database!")
except Exception as e:
    logger.warning(f"Could not connect to MySQL database ({e}). Falling back to local SQLite database.")
    DATABASE_URL = SQLITE_URL
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
