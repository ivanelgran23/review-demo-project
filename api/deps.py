from typing import Generator

from common.db import SessionLocal


def get_db() -> Generator:
    """Dependency to provide DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
