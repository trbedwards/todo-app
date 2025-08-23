from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    from .models import Task  # ensure models imported so table is created
    SQLModel.metadata.create_all(engine)

def get_session():
    """Yield a database session and ensure it's closed after use.

    When used as a FastAPI dependency, this will provide a session for the
    duration of the request and then close it. This prevents connection leaks
    that occurred when sessions were returned without being properly closed.
    """
    with Session(engine) as session:
        yield session
