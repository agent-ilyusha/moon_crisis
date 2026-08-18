from dotenv import load_dotenv

from os import getenv


load_dotenv()

username = getenv("DB_USER", "postgres")
password = getenv("DB_PASSWORD", "postgres")
host = getenv("DB_HOST", "db")
port = getenv("DB_PORT") or "5432"
database_name = getenv("DB_NAME", "lunar_game")
