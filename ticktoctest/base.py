import os

# Third party imports
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# package imports
from .models import Base

db_name = 'sqlite:///c:\\data\\sqlite\\db\\FreshTest.db'
DATABASE_URI = 'mysql+pymysql://TomRoot:Sporty66@mysql.stackcp.com:51228/ticktoctestDB-3637742e'

engine = create_engine(DATABASE_URI, pool_recycle=3000, echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
