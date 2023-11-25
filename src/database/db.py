import configparser
import pathlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings

file_config = pathlib.Path(__file__).parent.parent.parent.joinpath('config.ini')
config = configparser.ConfigParser()
config.read(file_config)

# user = config.get('DB', 'USER')
# password = config.get('DB', 'PASSWORD')
# database_name = config.get('DB', 'DB_NAME')
# domain = config.get('DB', 'DOMAIN')
# port = config.get('DB', 'PORT')

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()