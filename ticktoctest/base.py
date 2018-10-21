import os

# Third party imports
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# package imports
from .models import Base

db_name = 'sqlite:///c:\\data\\sqlite\\db\\FreshTest.db'
DATABASE_URI = db_name or os.environ.get('SQLALCHEMY_DATABASE_URL')

engine = create_engine(DATABASE_URI, pool_recycle=3600, echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
