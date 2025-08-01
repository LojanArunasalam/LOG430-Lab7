from django.db import models
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine 
from dotenv import load_dotenv
import logging
import os 

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)


load_dotenv()
DATABASE_URL_PRODUCTS = os.getenv("DATABASE_URL_PRODUCTS")

engine = create_engine(DATABASE_URL_PRODUCTS)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    description = Column(String)
    prix_unitaire = Column(Float)
    
    #Relationships
    # line_sale = relationship(LineSale)
    # stock = relationship(Stock)

    def __str__(self):
        return f"{self.name} - {self.category} - {self.prix_unitaire}"

