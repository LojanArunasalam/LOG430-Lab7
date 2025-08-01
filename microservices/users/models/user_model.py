from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine 
from dotenv import load_dotenv
import logging
import os 

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL_CUSTOMERS = os.getenv("DATABASE_URL_CUSTOMERS")

engine = create_engine(DATABASE_URL_CUSTOMERS)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)  # Added for customer accounts
    phone = Column(String)
    address = Column(String)

    def __str__(self):
        return f"{self.name} - ID: {self.id}"