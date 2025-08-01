from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine 
from dotenv import load_dotenv
import logging
import os 

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL_ECOMMERCE = os.getenv("DATABASE_URL_ECOMMERCE")

engine = create_engine(DATABASE_URL_ECOMMERCE)
Base = declarative_base()

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    total = Column(Float, default=0.0)
    user = Column(Integer, nullable=False)  # Assuming a user_id to identify the cart owner and use microservice for this
    store = Column(Integer, nullable=False)

    def __str__(self):
        return f"Cart ID: {self.id}, User ID: {self.user_id}, Total Price: {self.total_price}, Store ID: {self.store}"
