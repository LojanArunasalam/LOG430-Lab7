import logging
from models.product_model import Product

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

class ProductRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, id):
        logging.debug(f"Fetching product with id {id}")
        product = self.session.query(Product).filter_by(id=id).first()
        if not product:
            logging.warning(f"No prouduct found with id {id}")
            return None
        logging.debug(f"Fetched successfully product with id {id}")
        return product
    
    def get_all_products(self):
        logging.debug("Fetching all products")
        products = self.session.query(Product).all()
        if not products:
            logging.warning("No products found")
            return None
        logging.debug(f"Fetched successfully {len(products)} products")
        return products
    
    def get_product_by_category(self, category):
        logging.debug(f"Fetching products in category {category}")
        products = self.session.query(Product).filter_by(category=category).all()
        if not products:
            logging.warning(f"No products found in category {category}")
            return None
        logging.debug(f"Fetched successfully {len(products)} products in category {category}")
        
        return products
    
    def add_product(self, product):
        logging.debug(f"Adding product {product.name}")
        self.session.add(product)
        self.session.commit()
        logging.debug(f"Product {product.name} added successfully")
        
    def update_product(self, product):
        logging.debug(f"Updating product {product.id}")
        existing_product = self.get_by_id(self.session, product.id)
        if not existing_product:
            logging.error(f"Product with id {product.id} does not exist")
            return None
        existing_product.name = product.name
        existing_product.price = product.price
        existing_product.category = product.category
        self.session.commit()
        logging.debug(f"Product {product.id} updated successfully")
        
    def delete_product(self, product_id):
        logging.debug(f"Deleting product with id {product_id}")
        product = self.get_by_id(product_id)
        if not product:
            logging.error(f"Product with id {product_id} does not exist")
            return None
        self.session.delete(product)
        self.session.commit()
        logging.debug(f"Product with id {product_id} deleted successfully")