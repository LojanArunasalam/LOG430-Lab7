from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine 
from dotenv import load_dotenv
import logging
import os 

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL_WAREHOUSE = os.getenv("DATABASE_URL_WAREHOUSE")

engine = create_engine(DATABASE_URL_WAREHOUSE)
Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    quantite = Column(Integer)

    #Relationsips
    product = Column(Integer, nullable=False)
    store = Column(Integer, nullable=False)
