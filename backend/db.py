from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    from .models import Task  # ensure models imported so table is created
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
