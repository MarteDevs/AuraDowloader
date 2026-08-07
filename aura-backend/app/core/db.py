import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_env_settings

logger = logging.getLogger(__name__)

env = get_env_settings()

DB_NAME = env.db_name
DB_HOST = env.db_host
DB_PORT = env.db_port
DB_USER = env.db_user
DB_PASSWORD = env.db_password
MYSQL_URL = env.mysql_url
SQLITE_URL = "sqlite:///./aura_database.db"

# Append charset for MySQL connections (utf8mb4 covers emoji and full unicode).
if MYSQL_URL.startswith("mysql"):
    sep = "&" if "?" in MYSQL_URL else "?"
    MYSQL_URL = f"{MYSQL_URL}{sep}charset=utf8mb4"

DATABASE_URL = MYSQL_URL


def ensure_mysql_database() -> None:
    try:
        import pymysql
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connect_timeout=5,
        )
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        conn.commit()
        conn.close()
        logger.info(f"Ensured MySQL database '{DB_NAME}' exists.")
    except Exception as e:
        logger.warning(f"Could not auto-create MySQL database '{DB_NAME}': {e}")


ensure_mysql_database()

engine = None

try:
    logger.info(
        f"Attempting connection to primary database "
        f"({DATABASE_URL.split('@')[-1]})..."
    )
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    with engine.connect() as conn:
        logger.info(f"Successfully connected to MySQL database '{DB_NAME}'!")
except Exception as e:
    logger.warning(
        f"Could not connect to MySQL database ({e}). "
        f"Falling back to local SQLite database."
    )
    DATABASE_URL = SQLITE_URL
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
