from dotenv import load_dotenv
import logging
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL_ECOMMERCE = os.getenv("DATABASE_URL_ECOMMERCE")

engine = create_engine(DATABASE_URL_ECOMMERCE)
Base = declarative_base()


class Checkout(Base):
    __tablename__ = "checkout"

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, nullable=False)  # Reference to cart (no FK constraint for microservices)
    current_status = Column(String(50), nullable=False, default='pending')  # Status of the checkout
    
    def __str__(self):
        return f"Checkout {self.id} - Cart: {self.cart_id} - Status: {self.current_status}"
    
