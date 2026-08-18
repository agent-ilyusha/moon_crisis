from sqlalchemy import create_engine
<<<<<<< HEAD
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


=======
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker

from app.core.core import username, password, host, port, database_name


class Database:
    def __init__(self):
        self.engine = create_engine(
            f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_name}",
            echo=True
        )
        self.Session = sessionmaker(bind=self.engine)


if __name__ == '__main__':
    database = Database()
    print(database.Session)
    print(database.engine)
>>>>>>> 1ad351b05d98169fa8961cb9e6d17a2a16741fa2
