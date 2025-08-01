from repository import StoreRepository, StockRepository, ProductDepotRepository
import logging 
import requests

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

class StoreService:
    def __init__(self, session):
        self.session = session
        self.store_repository = StoreRepository(session)

    def get_store_by_id(self, store_id):
        store = self.store_repository.get_by_id(store_id)
        return store
    
    def get_all_stores(self):
        stores = self.store_repository.get_all_stores()
        return stores

    def add_store(self, store):
        self.store_repository.add_store(store)
        return store
    
    def update_store(self, store):
        updated_store = self.store_repository.update_store(store)
        return updated_store
    
    def delete_store(self, store_id):
        deleted_store = self.store_repository.delete_store(store_id)
        return deleted_store


class StockService:
    def __init__(self, session):
        self.session = session
        self.stock_repository = StockRepository(session)

    def get_stock_by_id(self, stock_id):
        stock = self.stock_repository.get_by_id(stock_id)
        return stock
    
    def get_stock_by_product_and_store(self, product_id, store_id):
        # Validate product exists in products service
        # if not self._validate_product_exists(product_id):
        #     logging.error(f"Product {product_id} does not exist")
        #     return None
        
        stock = self.stock_repository.get_by_product_and_store(product_id, store_id)
        return stock
    
    def get_all_stocks(self):
        stocks = self.stock_repository.get_all_stocks()
        return stocks
    
    def get_stocks_by_store(self, store_id):
        stocks = self.stock_repository.get_stocks_by_store(store_id)
        return stocks
    
    def get_stocks_by_product(self, product_id):
        # Validate product exists in products service
        if not self._validate_product_exists(product_id):
            logging.error(f"Product {product_id} does not exist")
            return None
        stocks = self.stock_repository.get_stocks_by_product(product_id)
        return stocks

    def add_stock(self, stock):
        # Validate product exists in products service
        if not self._validate_product_exists(stock.product):
            raise ValueError(f"Product {stock.product} does not exist")
        
        # Validate store exists locally
        store_service = StoreService(self.session)
        if not store_service.get_store_by_id(stock.store):
            raise ValueError(f"Store {stock.store} does not exist")
        
        self.stock_repository.add_stock(stock)
        return stock
    
    def update_stock_quantity(self, product_id, store_id, new_quantity):
        if new_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        updated_stock = self.stock_repository.update_stock_quantity(product_id, store_id, new_quantity)
        if not updated_stock:
            raise ValueError(f"Stock not found for product {product_id} in store {store_id}")
        return updated_stock
    
    def reduce_stock(self, product_id, store_id, quantity_to_reduce):
        if quantity_to_reduce <= 0:
            raise ValueError("Quantity to reduce must be positive")
        
        reduced_stock = self.stock_repository.reduce_stock(product_id, store_id, quantity_to_reduce)
        if not reduced_stock:
            raise ValueError("Insufficient stock or stock not found")
        return reduced_stock
    
    def increase_stock(self, product_id, store_id, quantity_to_increase):
        if quantity_to_increase <= 0:
            raise ValueError("Quantity to increase must be positive")
        
        increased_stock = self.stock_repository.increase_stock(product_id, store_id, quantity_to_increase)
        if not increased_stock:
            raise ValueError("Stock not found or insufficient stock")
        return increased_stock
    
    def delete_stock(self, stock_id):
        deleted_stock = self.stock_repository.delete_stock(stock_id)
        return deleted_stock
    
    def _validate_product_exists(self, product_id):
        try:
            response = requests.get(f"http://kong-api_gateway:8000/products/api/v1/products/{product_id}")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Failed to validate product {product_id}: {e}")
            return False


class ProductDepotService:
    def __init__(self, session):
        self.session = session
        self.depot_repository = ProductDepotRepository(session)

    def get_depot_by_id(self, depot_id):
        depot = self.depot_repository.get_by_id(depot_id)
        return depot
    
    def get_depot_by_product_id(self, product_id):
        # Validate product exists in products service
        if not self._validate_product_exists(product_id):
            logging.error(f"Product {product_id} does not exist")
            return None
        
        depot = self.depot_repository.get_by_product_id(product_id)
        return depot
    
    def get_all_depot_stocks(self):
        depots = self.depot_repository.get_all_depot_stocks()
        return depots

    def add_depot_stock(self, depot):
        # Validate product exists in products service
        if not self._validate_product_exists(depot.product_id):
            raise ValueError(f"Product {depot.product_id} does not exist")
        
        self.depot_repository.add_depot_stock(depot)
        return depot
    
    def update_depot_quantity(self, product_id, new_quantity):
        if new_quantity < 0:
            raise ValueError("Depot quantity cannot be negative")
        
        updated_depot = self.depot_repository.update_depot_quantity(product_id, new_quantity)
        if not updated_depot:
            raise ValueError(f"Depot stock not found for product {product_id}")
        return updated_depot
    
    def reduce_depot_stock(self, product_id, quantity_to_reduce):
        if quantity_to_reduce <= 0:
            raise ValueError("Quantity to reduce must be positive")
        
        reduced_depot = self.depot_repository.reduce_depot_stock(product_id, quantity_to_reduce)
        if not reduced_depot:
            raise ValueError("Insufficient depot stock or depot not found")
        return reduced_depot

    def increase_depot_stock(self, product_id, quantity_to_increase):
        if quantity_to_increase <= 0:
            raise ValueError("Quantity to reduce must be positive")
        
        reduced_depot = self.depot_repository.increase_depot_stock(product_id, quantity_to_increase)
        if not reduced_depot:
            raise ValueError("Insufficient depot stock or depot not found")
        return reduced_depot
    
    def delete_depot_stock(self, depot_id):
        deleted_depot = self.depot_repository.delete_depot_stock(depot_id)
        return deleted_depot

    def transfer_to_store(self, product_id, store_id, quantity):
        """Transfer stock from depot to store"""
        if quantity <= 0:
            raise ValueError("Transfer quantity must be positive")
        
        # Reduce depot stock
        depot_result = self.reduce_depot_stock(product_id, quantity)
        if not depot_result:
            raise ValueError("Failed to reduce depot stock")
        
        try:
            # Increase store stock
            stock_service = StockService(self.session)
            stock_result = stock_service.increase_stock(product_id, store_id, quantity)
            
            logging.info(f"Transferred {quantity} units of product {product_id} from depot to store {store_id}")
            return {
                'product_id': product_id,
                'store_id': store_id,
                'quantity_transferred': quantity,
                'remaining_depot_stock': depot_result.quantite_depot,
                'new_store_stock': stock_result.quantite
            }
        except Exception as e:
            # Rollback depot reduction if store increase fails
            self.increase_depot_stock(product_id, quantity)
            raise ValueError(f"Failed to transfer stock: {e}")
    
    def _validate_product_exists(self, product_id):
        """Validate product exists by calling products microservice"""
        try:
            response = requests.get(f"http://kong-api_gateway:8000/products/api/v1/products/{product_id}")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Failed to validate product {product_id}: {e}")
            return False


class WarehouseService:
    """Composite service for complex warehouse operations"""
    def __init__(self, session):
        self.session = session
        self.store_service = StoreService(session)
        self.stock_service = StockService(session)
        self.depot_service = ProductDepotService(session)

    def get_complete_inventory_info(self, product_id, store_id=None):
        """Get comprehensive inventory information for a product"""
        # Validate product exists
        if not self._validate_product_exists(product_id):
            raise ValueError(f"Product {product_id} does not exist")
        
        if store_id:
            # Get info for specific store
            return self.warehouse_repository.get_complete_stock_info(product_id, store_id)
        else:
            # Get info for all stores
            all_stores = self.store_service.get_all_stores()
            if not all_stores:
                return None
            
            inventory_info = []
            for store in all_stores:
                store_info = self.warehouse_repository.get_complete_stock_info(product_id, store.id)
                store_info['store_name'] = store.name
                inventory_info.append(store_info)
            
            # Add depot info
            depot_stock = self.depot_service.get_depot_by_product_id(product_id)
            depot_quantity = depot_stock.quantite_depot if depot_stock else 0
            
            return {
                'product_id': product_id,
                'depot_stock': depot_quantity,
                'stores': inventory_info,
                'total_system_stock': sum(info['total_available'] for info in inventory_info) + depot_quantity
            }
    
    def restock_store_from_depot(self, product_id, store_id, quantity):
        """Move stock from depot to store"""
        return self.depot_service.transfer_to_store(product_id, store_id, quantity)
    
    def get_low_stock_alerts(self, minimum_threshold=5):
        """Get products with low stock across all stores"""
        low_stock_items = []
        all_stocks = self.stock_service.get_all_stocks()
        
        if all_stocks:
            for stock in all_stocks:
                if stock.quantite <= minimum_threshold:
                    # Get product info
                    product_info = self._get_product_info(stock.product)
                    store_info = self.store_service.get_store_by_id(stock.store)
                    
                    low_stock_items.append({
                        'product_id': stock.product_id,
                        'product_name': product_info.get('name', 'Unknown'),
                        'store_id': stock.store,
                        'store_name': store_info.name if store_info else 'Unknown',
                        'current_stock': stock.quantite,
                        'threshold': minimum_threshold
                    })
        
        return low_stock_items
    
    def _validate_product_exists(self, product_id):
        """Validate product exists by calling products microservice"""
        try:
            response = requests.get(f"http://kong-api_gateway:8000/products/api/v1/products/{product_id}")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Failed to validate product {product_id}: {e}")
            return False
    
    def _get_product_info(self, product_id):
        """Get product information from products microservice"""
        try:
            response = requests.get(f"http://kong-api_gateway:8000/products/api/v1/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logging.error(f"Failed to get product info for {product_id}: {e}")
            return {}