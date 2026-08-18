from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.core import database_name, host, password, port, username

SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True
)
Session = sessionmaker(bind=engine)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


