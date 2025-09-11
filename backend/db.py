import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment or use SQLite default
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Check if we're in a deployment environment (Render)
    if os.getenv("RENDER"):
        # Use in-memory SQLite for Render deployment
        DATABASE_URL = "sqlite:///:memory:"
    else:
        # Use file-based SQLite for local development
        DATABASE_URL = "sqlite:///./data/dev.db"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
