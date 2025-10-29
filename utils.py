import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session


load_dotenv()

# defaults to sqlite if there's no db available
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///countries.db")

engine = create_engine(
    pool_size=5,
    max_overflow=10,
    url=DATABASE_URL,
    echo=True,  # set to false in production
    # connect_args={"check_same_thread": False}
    )


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
