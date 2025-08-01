import logging
from ..models import Product, LineSale, Sale, Store, Product_Depot
from ..repositories.product_repository import ProductRepository
from ..repositories.sale_repository import SaleRepository
from ..repositories.stock_repository import StockRepository
import requests

class DomainService: 
    def __init__(self, session):
        self.session = session
        self.product_repository = ProductRepository(session)
        self.sale_repository = SaleRepository(session)
        self.stock_repository = StockRepository(session)


    def restock_from_depot(self, product_id, quantity, store_id):
        try:
            response = requests.post(
            f"http://localhost:8000/warehouse/api/v1/depot/transfer",
            json={
                'product': product_id,
                'store': store_id,
                'quantity': quantity
                }
            )
        
            if response.status_code == 200:
                return {
                    'success': True,
                    **response.json()
                }
        except: 
            logging.error(f"Erreur transfert stock: {e}")
            return {
                'success': False,
                'error': f"Erreur connexion microservice warehouse: {e}"
            }
    def get_product_with_stocks(self, store_id):
        
        # 1. Récupérer tous les produits via microservice products
        products = self._get_all_products_from_microservice()
        
        if not products:
            logging.warning("Aucun produit récupéré du microservice, utilisation fallback")
            raise Exception("Aucune produit")
        
        # 2. Récupérer stocks par magasin via microservice warehouse
        stocks = self._get_stocks_by_store_from_microservice(store_id)
        
        # 3. Associer produits et stocks
        products_with_stocks = []
        for product in products:
            # Trouver le stock correspondant pour ce produit
            product_stock = None
            for stock in stocks:
                if stock.get('product') == product.get('id'):
                    product_stock = stock
                    break
            
            # Si pas de stock trouvé, créer un objet stock vide
            if not product_stock:
                product_stock = {
                    'id': None,
                    'product': product.get('id'),
                    'store': store_id,
                    'quantite': 0
                }
            
            products_with_stocks.append((product, product_stock))
        
        return products_with_stocks

    def performances(self):
        # Generate the total in sales for each stores, and for each stock of the products in each store, indicates whether the stock is sufficient or not.
        stores = Store.get_all_stores(self.session)
        totals = []
        stocks = []
        store_ids = []
        for store in stores:
            sales = self.sale_repository.get_sales_by_store(store.id)
            total_store = sum(sale.total for sale in sales)
            totals.append(total_store)
            stocks_store = self.stock_repository.get_stock_by_store(self.session, store.id)
            stocks.append(stocks_store)
            store_ids.append(store.id)


        performances_data = zip(totals, stocks, store_ids)
        return performances_data

    def generate_report(self, store_id):
        report = {}
        sales = self.sale_repository.get_sales_by_store(store_id)
        most_sold_product = None
        max_quantity = 0
            
        for sale in sales:
            line_sales = LineSale.get_line_sales_by_sale(self.session, sale.id)
            for line_sale in line_sales:
                if line_sale.quantite > max_quantity:
                    max_quantity = line_sale.quantite
                    most_sold_product = self.product_repository.get_by_id(line_sale.product)

        report["store_id"] = store_id
        report["sales"] = sales
        report["most_sold_product"] = most_sold_product
        report["max_quantity"] = max_quantity

        return report

    def _get_all_products_from_microservice(self):
        """Récupérer tous les produits via microservice products"""
        try:
            response = requests.get(f"http://localhost:8000/products/api/v1/products")
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Erreur récupération produits: HTTP {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"Erreur connexion microservice products: {e}")
            return None

    def _get_stocks_by_store_from_microservice(self, store_id):
        """Récupérer stocks par magasin via microservice warehouse"""
        try:
            response = requests.get(f"http://localhost:8000/warehouse/api/v1/stocks/store/{store_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Erreur récupération stocks: HTTP {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"Erreur connexion microservice warehouse: {e}")
            return []