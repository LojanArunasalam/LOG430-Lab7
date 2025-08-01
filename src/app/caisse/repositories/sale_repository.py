import logging
from ..models import Sale

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

class SaleRepository:
    def __init__(self, session):
        self.session = session

    def get_sales_by_store(self, store_id):
        logging.debug(f"Fetching sales for store id {store_id}")
        sales = self.session.query(Sale).filter_by(store=store_id).all()
        if not sales:
            logging.warning(f"No sales found for store id {store_id}")
            return None
        logging.debug(f"Fetched successfully {len(sales)} sales for store id {store_id}")
        return sales
    
    def get_sales_by_user(self, user_id):
        logging.debug(f"Fetching sales for user id {user_id}")
        sales = self.session.query(Sale).filter_by(user=user_id).all()
        if not sales:
            logging.warning(f"No sales found for user id {user_id}")
            return None
        logging.debug(f"Fetched successfully {len(sales)} sales for user id {user_id}")
        return sales
    
    def get_all_sales(self):
        logging.debug("Fetching all sales")
        sales = self.session.query(Sale).all()
        if not sales:
            logging.warning("No sales found")
            return None
        logging.debug(f"Fetched successfully {len(sales)} sales")
        return sales
    
    def add_sale(self, sale):
        logging.debug(f"Adding Sale with total {sale.total} for store {sale.store}")
        self.session.add(sale)
        self.session.commit()
        logging.debug(f"Sale with total {sale.total} added successfully for store {sale.store}")
        return sale
    
