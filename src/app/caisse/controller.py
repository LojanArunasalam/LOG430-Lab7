from .models import Product, Stock, Sale, LineSale, Store, User, Product_Depot, engine 
from sqlalchemy.orm import sessionmaker
import logging
from .services.product_service import ProductService
from .services.sale_service import SaleService
from .services.stock_service import StockService
from caisse.services.domain_service import DomainService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

Session = sessionmaker(bind=engine)
session = Session()

class MainController:
    def __init__(self):
        self.domaine_service = DomainService(session)

    def restock_from_depot(self, product_id, quantity, store_id):
        self.domaine_service.restock_from_depot(product_id, quantity, store_id)

    def get_product_with_stocks(self, store_id):
        return self.domaine_service.get_product_with_stocks(store_id)

    def performances(self):
        return self.domaine_service.performances()

    def generate_report(self, store_id):
        return self.domaine_service.generate_report(store_id)


