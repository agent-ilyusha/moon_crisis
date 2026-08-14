from sqlalchemy import create_engine
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
