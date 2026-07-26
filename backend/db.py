import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

db_url=os.getenv("DATABASE_URL")

engine = create_engine(db_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session(): #Return session to be used by FastAPI
    with Session(engine) as session:
        yield session