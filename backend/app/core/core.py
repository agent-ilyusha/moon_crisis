from dotenv import load_dotenv

from os import getenv


load_dotenv()

username = getenv('USER')
password = getenv('PASSWORD')
host = getenv('HOST')
port = getenv('PORT')
database_name = getenv('DATABASE_NAME')
