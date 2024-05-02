# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "mysql+mysqlconnector://vinyl_record_store:gnZYcu\*e)KrTc2h@34.121.144.172:3306/vinyl_record_store"

# engine = create_engine(DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()



from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

# initialize Cloud SQL Connector
connector = Connector()

# SQLAlchemy database connection creator function
def getconn():
    conn = connector.connect(
        "visitasguiadas-219322:us-central1:root", # Cloud SQL Instance Connection Name
        "pymysql",
        user="vinyl_record_store",
        password="gnZYcu\*e)KrTc2h",
        db="vinyl_record_store",
        ip_type=IPTypes.PUBLIC # IPTypes.PRIVATE for private IP
    )
    return conn

engine = create_engine(
   "mysql+pymysql://",
    creator=getconn,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

