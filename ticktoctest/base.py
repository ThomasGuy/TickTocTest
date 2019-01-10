# Third party imports
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


# package imports
from .models import Base

db_name = 'sqlite:///c:\\data\\sqlite\\db\\tickToc15m.db'
DATABASE_URI = 'mysql+pymysql://TomRoot:Sporty66@mysql.stackcp.com:51228/ticktoctestDB-3637742e'
master = f'sqlite:///c:\\data\\sqlite\\db\\master_db.db'

engine = create_engine(DATABASE_URI, pool_recycle=3000, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
