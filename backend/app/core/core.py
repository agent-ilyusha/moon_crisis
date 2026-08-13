from dotenv import load_dotenv

from os import getenv


load_dotenv()

user = getenv('USER')
password = getenv('PASSWORD')
host = getenv('HOST')
port = getenv('PORT')
database = getenv('DATABASE_NAME')
