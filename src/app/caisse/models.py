from django.db import models
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine 
from dotenv import load_dotenv
import logging
import os 

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class LineSale(Base):
    __tablename__ = "line_sales" 

    id = Column(Integer, primary_key=True)
    quantite = Column(Integer)
    prix = Column(Float)

    #Relationships
    sale = Column(Integer, ForeignKey("sales.id"))
    product = Column(Integer, ForeignKey("products.id"))

    def __str__(self):
        return f"Product ID: {self.product} - Quantity: {self.quantite} - Price: {self.prix}"

    @classmethod
    def get_by_id(cls, session, id):
        logging.debug(f"Fetching line sale with id {id}")
        line_sale = session.query(cls).filter_by(id=id).first()
        if not line_sale:
            logging.warning(f"LineSale with id {id} not found")
            return None
        logging.debug(f"Fetched succesfully LineSale with id {id}")
        return line_sale
    
    @classmethod
    def get_line_sales_by_sale(cls, session, sale_id):
        logging.debug(f"Fetching line sales for sale id {sale_id}")
        line_sales = session.query(cls).filter_by(sale=sale_id).all()
        if not line_sales:
            logging.warning(f"No line sales found for sale id {sale_id}") 
            return None  
        logging.debug(f"Fetched successfully {len(line_sales)} line sales for sale id {sale_id}")
        return line_sales
    

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    quantite = Column(Integer, primary_key=True)

    #Relationsips
    product = Column(Integer, ForeignKey("products.id"))
    store = Column(Integer, ForeignKey("stores.id"))

    def __str__(self):
        return f"{self.product} - {self.quantite}"

    @classmethod
    def get_stock_by_id(cls, session, id):
        logging.debug(f"Fetching stock with id {id}")
        stock = session.query(cls).filter_by(id=id).first()
        if not stock:
            logging.warning(f"No stock found with id {id}")
            return None
        logging.debug(f"Fetched successfully stock with id {id}")
        return stock
    
    @classmethod
    def get_stock_by_store(cls, session, store_id):
        logging.debug(f"Fetching stocks for store id {store_id}")
        stocks = session.query(cls).filter_by(store=store_id).all()
        if not stocks:
            logging.warning(f"No stocks found for store id {store_id}")
            return None
        logging.debug(f"Fetched successfully {len(stocks)} stocks for store id {store_id}")
        return stocks
    
    @classmethod
    def get_stock_by_product_and_store(cls, session, product_id, store_id):
        logging.debug(f"Fetching stock for product id {product_id} in store id {store_id}")
        stock = session.query(cls).filter_by(product=product_id, store=store_id).first()
        if not stock:
            logging.warning(f"No Stock for product id {product_id} in store id {store_id} not found")
            return None
        logging.debug(f"Fetched successfully stock for product id {product_id} in store id {store_id}")
        return stock
        

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    description = Column(String)
    prix_unitaire = Column(Float)
    
    #Relationships
    line_sale = relationship(LineSale)
    stock = relationship(Stock)

    def __str__(self):
        return f"{self.name} - {self.category} - {self.prix_unitaire}"

    @classmethod
    def get_by_id(cls, session, id):
        logging.debug(f"Fetching product with id {id}")
        product = session.query(cls).filter_by(id=id).first()
        if not product:
            logging.warning(f"No prouduct found with id {id}")
            return None
        logging.debug(f"Fetched successfully product with id {id}")
        return product
    
    @classmethod
    def get_all_products(cls, session):
        logging.debug("Fetching all products")
        products = session.query(cls).all()
        if not products:
            logging.warning("No products found")
            return None
        logging.debug(f"Fetched successfully {len(products)} products")
        return products
    
    @classmethod
    def get_product_by_category(cls, session, category):
        logging.debug(f"Fetching products in category {category}")
        products = session.query(cls).filter_by(category=category).all()
        if not products:
            logging.warning(f"No products found in category {category}")
            return None
        logging.debug(f"Fetched successfully {len(products)} products in category {category}")
        return products


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total = Column(Float)

    #Relationships
    line_vente = relationship(LineSale)
    user = Column(ForeignKey("users.id"))
    store = Column(ForeignKey("stores.id"))

    def __str__(self):
        return f"Sale {self.id} - Total: {self.total}"    

    @classmethod
    def get_sales_by_store(cls, session, store_id):
        logging.debug(f"Fetching sales for store id {store_id}")
        sales = session.query(cls).filter_by(store=store_id).all()
        if not sales:
            logging.warning(f"No sales found for store id {store_id}")
            return None
        logging.debug(f"Fetched successfully {len(sales)} sales for store id {store_id}")
        return sales
    
    @classmethod
    def get_sales_by_user(cls, session, user_id):
        logging.debug(f"Fetching sales for user id {user_id}")
        sales = session.query(cls).filter_by(user=user_id).all()
        if not sales:
            logging.warning(f"No sales found for user id {user_id}")
            return None
        logging.debug(f"Fetched successfully {len(sales)} sales for user id {user_id}")
        return sales
    
    @classmethod
    def get_all_sales(cls, session):
        logging.debug("Fetching all sales")
        sales = session.query(cls).all()
        if not sales:
            logging.warning("No sales found")
            return None
        logging.debug(f"Fetched successfully {len(sales)} sales")
        return sales

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    #Relationships
    sale = relationship(Sale)

    def __str__(self):
        return f"{self.name} - ID: {self.id}"

    @classmethod
    def get_user_by_id(cls, session, id):
        logging.debug(f"Fetching user with id {id}")
        user = session.query(cls).filter_by(id=id).first()
        if not user:
            logging.warning(f"No user found with id {id}")
            return None
        logging.debug(f"Fetched successfully user with id {id}")
        return user
    
    @classmethod
    def get_all_users(cls, session):
        logging.debug("Fetching all users")
        users = session.query(cls).all()
        if not users:
            logging.warning("No users found")
            return None
        logging.debug(f"Fetched successfully {len(users)} users")
        return users
    

class Product_Depot(Base):
    __tablename__ = "products_depot"

    id = Column(Integer, primary_key=True)
    quantite_depot = Column(Integer)
    #Relationships
    product = Column(ForeignKey("products.id"))

    @classmethod
    def get_product_depot_by_product_id(cls, session, product_id):
        logging.debug(f"Fetching product depot for product id {product_id}")
        product_depot = session.query(cls).filter_by(id=product_id).first()
        if not product_depot:
            logging.warning(f"No product depot found for product id {product_id}")
            return None
        logging.debug(f"Fetched successfully product depot for product id {product_id}")
        return product_depot
    
    @classmethod
    def get_all_product_depots(cls, session):
        logging.debug("Fetching all product depots")
        product_depots = session.query(cls).all()
        if not product_depots:
            logging.warning("No product depots found")  
            return None
        logging.debug(f"Fetched successfully {len(product_depots)} product depots")
        return product_depots


class Store(Base):
    # Includes the parent house (maison mere)
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    #Relationships
    stocks = relationship(Stock)
    sales = relationship(Sale)

    def __str__(self):
        return f"{self.name} - ID: {self.id}"

    @classmethod
    def get_store_by_id(cls, session, id):
        logging.debug(f"Fetching store with id {id}")
        store = session.query(cls).filter_by(id=id).first()
        if not store:
            logging.warning(f"No store found with id {id}")
            return None
        logging.debug(f"Fetched successfully store with id {id}")
        return store
    
    @classmethod
    def get_all_stores(cls, session):
        logging.debug("Fetching all stores")
        stores = session.query(cls).all()
        if not stores:
            logging.warning("No stores found")
            return None
        logging.debug(f"Fetched successfully {len(stores)} stores")
        return stores
    
    @classmethod
    def get_stores_by_name(cls, session, name):
        logging.debug(f"Fetching store with name {name}")
        store = session.query(cls).filter_by(name=name).first()
        if not store:
            logging.warning(f"No store found with name {name}")
            return None
        logging.debug(f"Fetched successfully store with name {name}")
        return store
    
# Will create the database + the tables associated with it
Base.metadata.create_all(engine)