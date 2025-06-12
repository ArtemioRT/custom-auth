# auth_server/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

#  ← Quitamos DATABASE_URL
# engine = create_engine(os.getenv("DATABASE_URL"), pool_pre_ping=True)

# Usamos un fichero SQLite local (se crea automáticamente)
engine = create_engine(
    "sqlite:///./auth.db",
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
