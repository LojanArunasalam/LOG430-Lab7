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

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __str__(self):
        return f"{self.name} - ID: {self.id}"