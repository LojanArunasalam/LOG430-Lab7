import logging
from models.store_model import Store
from models.stock_model import Stock
from models.product_depot_model import Product_Depot

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

class StoreRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, store_id):
        logging.debug(f"Fetching store with id {store_id}")
        store = self.session.query(Store).filter_by(id=store_id).first()
        if not store:
            logging.warning(f"No store found with id {store_id}")
            return None
        logging.debug(f"Fetched successfully store with id {store_id}")
        return store
    
    def get_all_stores(self):
        logging.debug("Fetching all stores")
        stores = self.session.query(Store).all()
        if not stores:
            logging.warning("No stores found")
            return None
        logging.debug(f"Fetched successfully {len(stores)} stores")
        return stores
    
    def add_store(self, store):
        logging.debug(f"Adding store {store.name}")
        self.session.add(store)
        self.session.commit()
        logging.debug(f"Store {store.name} added successfully")
        
    def update_store(self, store):
        logging.debug(f"Updating store {store.id}")
        existing_store = self.get_by_id(store.id)
        if not existing_store:
            logging.error(f"Store with id {store.id} does not exist")
            return None
        existing_store.name = store.name
        self.session.commit()
        logging.debug(f"Store {store.id} updated successfully")
        return existing_store
        
    def delete_store(self, store_id):
        logging.debug(f"Deleting store with id {store_id}")
        store = self.get_by_id(store_id)
        if not store:
            logging.error(f"Store with id {store_id} does not exist")
            return None
        self.session.delete(store)
        self.session.commit()
        logging.debug(f"Store with id {store_id} deleted successfully")
        return store


class StockRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, stock_id):
        logging.debug(f"Fetching stock with id {stock_id}")
        stock = self.session.query(Stock).filter_by(id=stock_id).first()
        if not stock:
            logging.warning(f"No stock found with id {stock_id}")
            return None
        logging.debug(f"Fetched successfully stock with id {stock_id}")
        return stock
    
    def get_by_product_and_store(self, product_id, store_id):
        logging.debug(f"Fetching stock for product {product_id} in store {store_id}")
        stock = self.session.query(Stock).filter_by(product=product_id, store=store_id).first()
        if not stock:
            logging.warning(f"No stock found for product {product_id} in store {store_id}")
            return None
        logging.debug(f"Fetched successfully stock for product {product_id} in store {store_id}")
        return stock
    
    def get_all_stocks(self):
        logging.debug("Fetching all stocks")
        stocks = self.session.query(Stock).all()
        if not stocks:
            logging.warning("No stocks found")
            return None
        logging.debug(f"Fetched successfully {len(stocks)} stocks")
        return stocks
    
    def get_stocks_by_store(self, store_id):
        logging.debug(f"Fetching all stocks for store {store_id}")
        stocks = self.session.query(Stock).filter_by(store=store_id).all()
        if not stocks:
            logging.warning(f"No stocks found for store {store_id}")
            return None
        logging.debug(f"Fetched successfully {len(stocks)} stocks for store {store_id}")
        return stocks
    
    def get_stocks_by_product(self, product_id):
        logging.debug(f"Fetching all stocks for product {product_id}")
        stocks = self.session.query(Stock).filter_by(product=product_id).all()
        if not stocks:
            logging.warning(f"No stocks found for product {product_id}")
            return None
        logging.debug(f"Fetched successfully {len(stocks)} stocks for product {product_id}")
        return stocks
    
    def add_stock(self, stock):
        logging.debug(f"Adding stock for product {stock.product} in store {stock.store}")
        self.session.add(stock)
        self.session.commit()
        logging.debug(f"Stock for product {stock.product} added successfully")
        
    def update_stock_quantity(self, product_id, store_id, new_quantity):
        logging.debug(f"Updating stock quantity for product {product_id} in store {store_id}")
        stock = self.get_by_product_and_store(product_id, store_id)
        if not stock:
            logging.error(f"Stock not found for product {product_id} in store {store_id}")
            return None
        stock.quantite = new_quantity
        self.session.commit()
        logging.debug(f"Stock quantity updated to {new_quantity}")
        return stock
    
    def reduce_stock(self, product_id, store_id, quantity_to_reduce):
        logging.debug(f"Reducing stock by {quantity_to_reduce} for product {product_id} in store {store_id}")
        stock = self.get_by_product_and_store(product_id, store_id)
        if not stock:
            logging.error(f"Stock not found for product {product_id} in store {store_id}")
            return None
        if stock.quantite < quantity_to_reduce:
            logging.error(f"Insufficient stock. Available: {stock.quantite}, Requested: {quantity_to_reduce}")
            return None
        stock.quantite -= quantity_to_reduce
        self.session.commit()
        logging.debug(f"Stock reduced by {quantity_to_reduce}. New quantity: {stock.quantite}")
        return stock
    
    def increase_stock(self, product_id, store_id, quantity_to_add):
        logging.debug(f"Increasing stock by {quantity_to_add} for product {product_id} in store {store_id}")
        stock = self.get_by_product_and_store(product_id, store_id)
        if not stock:
            # Create new stock entry if doesn't exist
            logging.debug(f"No existing stock found, creating new entry")
            from models.stock_model import Stock
            stock = Stock(product=product_id, store=store_id, quantite=quantity_to_add)
            self.session.add(stock)
        else:
            stock.quantite += quantity_to_add
        self.session.commit()
        logging.debug(f"Stock increased by {quantity_to_add}. New quantity: {stock.quantite}")
        return stock
        
    def delete_stock(self, stock_id):
        logging.debug(f"Deleting stock with id {stock_id}")
        stock = self.get_by_id(stock_id)
        if not stock:
            logging.error(f"Stock with id {stock_id} does not exist")
            return None
        self.session.delete(stock)
        self.session.commit()
        logging.debug(f"Stock with id {stock_id} deleted successfully")
        return stock


class ProductDepotRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, depot_id):
        logging.debug(f"Fetching product depot with id {depot_id}")
        depot = self.session.query(Product_Depot).filter_by(id=depot_id).first()
        if not depot:
            logging.warning(f"No product depot found with id {depot_id}")
            return None
        logging.debug(f"Fetched successfully product depot with id {depot_id}")
        return depot
    
    def get_by_product_id(self, product_id):
        logging.debug(f"Fetching depot stock for product {product_id}")
        depot = self.session.query(Product_Depot).filter_by(product=product_id).first()
        if not depot:
            logging.warning(f"No depot stock found for product {product_id}")
            return None
        logging.debug(f"Fetched successfully depot stock for product {product_id}")
        return depot
    
    def get_all_depot_stocks(self):
        logging.debug("Fetching all depot stocks")
        depots = self.session.query(Product_Depot).all()
        if not depots:
            logging.warning("No depot stocks found")
            return None
        logging.debug(f"Fetched successfully {len(depots)} depot stocks")
        return depots
    
    def add_depot_stock(self, depot):
        logging.debug(f"Adding depot stock for product {depot.product_id}")
        self.session.add(depot)
        self.session.commit()
        logging.debug(f"Depot stock for product {depot.product_id} added successfully")
        
    def update_depot_quantity(self, product_id, new_quantity):
        logging.debug(f"Updating depot quantity for product {product_id}")
        depot = self.get_by_product_id(product_id)
        if not depot:
            logging.error(f"Depot stock not found for product {product_id}")
            return None
        depot.quantite_depot = new_quantity
        self.session.commit()
        logging.debug(f"Depot quantity updated to {new_quantity}")
        return depot
    
    def reduce_depot_stock(self, product_id, quantity_to_reduce):
        logging.debug(f"Reducing depot stock by {quantity_to_reduce} for product {product_id}")
        depot = self.get_by_product_id(product_id)
        if not depot:
            logging.error(f"Depot stock not found for product {product_id}")
            return None
        if depot.quantite_depot < quantity_to_reduce:
            logging.error(f"Insufficient depot stock. Available: {depot.quantite_depot}, Requested: {quantity_to_reduce}")
            return None
        depot.quantite_depot -= quantity_to_reduce
        self.session.commit()
        logging.debug(f"Depot stock reduced by {quantity_to_reduce}. New quantity: {depot.quantite_depot}")
        return depot
    
    def increase_depot_stock(self, product_id, quantity_to_add):
        logging.debug(f"Increasing depot stock by {quantity_to_add} for product {product_id}")
        depot = self.get_by_product_id(product_id)
        if not depot:
            # Create new depot entry if doesn't exist
            logging.debug(f"No existing depot stock found, creating new entry")
            from models.stock_model import ProductDepot
            depot = ProductDepot(product_id=product_id, quantite_depot=quantity_to_add)
            self.session.add(depot)
        else:
            depot.quantite_depot += quantity_to_add
        self.session.commit()
        logging.debug(f"Depot stock increased by {quantity_to_add}. New quantity: {depot.quantite_depot}")
        return depot
        
    def delete_depot_stock(self, depot_id):
        logging.debug(f"Deleting depot stock with id {depot_id}")
        depot = self.get_by_id(depot_id)
        if not depot:
            logging.error(f"Depot stock with id {depot_id} does not exist")
            return None
        self.session.delete(depot)
        self.session.commit()
        logging.debug(f"Depot stock with id {depot_id} deleted successfully")
        return depot
