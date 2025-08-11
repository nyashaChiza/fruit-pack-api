import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:////var/data/app.db"  # Persistent disk path on Render

# Extract actual file path from the URL
db_file_path = DATABASE_URL.replace("sqlite:///", "")
db_dir = os.path.dirname(db_file_path)

try:
    # Create the directory if it doesn't exist
    os.makedirs(db_dir, exist_ok=True)
except Exception as e:
    print(e)
    DATABASE_URL = "sqlite:///db.sqlite3"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
