import logging
from ..models import Stock

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

class StockRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, session, id):
        logging.debug(f"Fetching stock with id {id}")
        stock = session.query(Stock).filter_by(id=id).first()
        if not stock:
            logging.warning(f"No stock found with id {id}")
            return None
        logging.debug(f"Fetched successfully stock with id {id}")
        return stock

    def get_all_stocks(self, session):
        logging.debug("Fetching all stocks")
        stocks = session.query(Stock).all()
        if not stocks:
            logging.warning("No stocks found")
            return None
        logging.debug(f"Fetched successfully {len(stocks)} stocks")
        return stocks

    def get_stock_by_store(self, session, store_id):
        logging.debug(f"Fetching stocks for store id {store_id}")
        stocks = session.query(Stock).filter_by(store=store_id).all()
        if not stocks:
            logging.warning(f"No stocks found for store id {store_id}")
            return None
        logging.debug(f"Fetched successfully {len(stocks)} stocks for store id {store_id}")
        return stocks
    
    def get_stock_by_product_and_store(self, session, product_id, store_id):
        logging.debug(f"Fetching stock for product id {product_id} in store id {store_id}")
        stock = session.query(Stock).filter_by(product=product_id, store=store_id).first()
        if not stock:
            logging.warning(f"No Stock for product id {product_id} in store id {store_id} not found")
            return None
        logging.debug(f"Fetched successfully stock for product id {product_id} in store id {store_id}")
        return stock