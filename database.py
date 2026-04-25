from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print(os.getenv('DBUSERNAME'))

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv('DBUSERNAME'),
    password=os.getenv('DBPASSWORD'),
    host=os.getenv('DBHOST'),
    database=os.getenv('DBNAME')
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()