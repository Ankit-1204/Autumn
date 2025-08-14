from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
import os

DATABASE_URL=os.getenv(
    "DATABASE_URL",
    "postgresql://myuser:mypassword@db:5432/workflow_db"
)

engine=create_engine(
    DATABASE_URL
)

# used to interact with DB 
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

# this is the base class for all db model
Base=declarative_base()
