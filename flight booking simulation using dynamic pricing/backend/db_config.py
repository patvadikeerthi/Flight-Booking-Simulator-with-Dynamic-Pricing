# backend/db_config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
load_dotenv()  # read .env from project root if present

# Provide DB URL as environment variable: DATABASE_URL
# Example: postgresql+psycopg2://username:password@localhost:5432/flightdb
DATABASE_URL = "sqlite:///./DB/flight_booking.db"
#DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/flightdb")

# SQLAlchemy engine & session factory
engine = create_engine(DATABASE_URL, future=True, echo=False, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

def get_session():
    """
    Use as:
      with get_session() as session:
          ...
    """
    return SessionLocal()
