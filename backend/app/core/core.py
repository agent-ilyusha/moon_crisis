<<<<<<< HEAD
from os import getenv

from dotenv import load_dotenv

load_dotenv()

username = getenv("DB_USER", "postgres")
password = getenv("DB_PASSWORD", "postgres")
host = getenv("DB_HOST", "db")
port = getenv("DB_PORT") or "5432"
database_name = getenv("DB_NAME", "lunar_game")
=======
from dotenv import load_dotenv

from os import getenv


load_dotenv()

username = getenv('USER')
password = getenv('PASSWORD')
host = getenv('HOST')
port = getenv('PORT')
database_name = getenv('DATABASE_NAME')
>>>>>>> 1ad351b05d98169fa8961cb9e6d17a2a16741fa2
