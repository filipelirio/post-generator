from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# engine = create_engine(settings.DATABASE_URL)
# Para SQLite, precisamos de check_same_thread=False
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args,
    echo=True if settings.LOG_LEVEL == "DEBUG" else False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependência do FastAPI para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
