import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_url = os.getenv("DATABASE_URL", "postgresql://smada:smada@localhost:5432/fastapi")
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
