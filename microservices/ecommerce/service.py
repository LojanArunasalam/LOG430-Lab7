from repository import CartRepository, ItemCartRepository, CheckoutRepository
import logging 
import requests
logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

class CartService:
    def __init__(self, session):
        self.session = session
        self.cart_repository = CartRepository(session)
        self.item_repository = ItemCartRepository(session)

    def get_cart_by_id(self, cart_id):
        cart = self.cart_repository.get_by_id(cart_id)
        return cart
    
    def get_cart_by_user(self, user_id):
        cart = self.cart_repository.get_by_user_id(user_id)
        return cart
    
    def get_or_create_cart(self, user_id, store_id):
        """Obtenir ou créer un panier pour l'utilisateur"""
        cart = self.cart_repository.get_by_user_and_store(user_id, store_id)
        if not cart:
            cart = self.cart_repository.create_cart(user_id, store_id)
        return cart

    def get_cart_with_items(self, cart_id):
        """Obtenir le panier avec tous ses articles"""
        # 1. Get the cart
        cart = self.cart_repository.get_by_id(cart_id)
        if not cart:
            return None
        
        # 2. Get all items for this cart
        items = self.item_repository.get_items_by_cart_id(cart_id)
        
        # 3. Calculate total
        calculated_total = sum(item.prix for item in items)
        
        # 4. Return cart data structure
        return {
            'cart': cart,
            'items': items,
            'item_count': len(items),
            'calculated_total': calculated_total
        }
    def add_item_to_cart(self, cart, product_id, quantity, store_id):
        """Ajouter un article au panier avec validation complète"""
        user_id = 0  # Assuming a default user_id for now
        product_info = self._get_product_info(product_id)
        if not product_info:
            raise ValueError(f"Produit {product_id} non trouvé")
            
        if not self._check_stock_availability(product_id, store_id, quantity):
            raise ValueError(f"Stock insuffisant pour le produit {product_id}")
            
        cart = self.get_or_create_cart(user_id, store_id)
        
        item = self.item_repository.add_item_to_cart(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            price=product_info.get('prix_unitaire'),
        )
        
        # 6. Mettre à jour le total du panier
        self._update_cart_total(cart.id)
        
        return item
    
    def update_item_quantity(self, item_id, new_quantity):
        """Mettre à jour la quantité d'un article dans le panier"""
        item = self.item_repository.get_by_id(item_id)
        if not item:
            raise ValueError(f"Article {item_id} non trouvé")
        
        # Obtenir le prix unitaire du produit
        product_info = self._get_product_info(item.product_id)
        if not product_info:
            raise ValueError(f"Impossible d'obtenir les informations du produit")
        
        updated_item = self.item_repository.update_item_quantity(
            item_id, new_quantity, product_info['prix_unitaire']
        )
        
        # Mettre à jour le total du panier
        self._update_cart_total(item.sale_id)
        
        return updated_item
    
    def remove_item_from_cart(self, item_id):
        """Supprimer un article du panier"""
        item = self.item_repository.get_by_id(item_id)
        if not item:
            raise ValueError(f"Article {item_id} non trouvé")
        
        cart_id = item.sale_id
        removed_item = self.item_repository.remove_item_from_cart(item_id)
        
        # Mettre à jour le total du panier
        self._update_cart_total(cart_id)
        
        return removed_item
    
    # def get_cart_with_items(self, cart_id):
    #     """Obtenir le panier avec tous ses articles"""
    #     ecommerce_repo = EcommerceRepository(self.session)
    #     return ecommerce_repo.get_cart_with_items(cart_id)
    
    def clear_cart(self, cart_id):
        """Vider le panier"""
        cleared_count = self.item_repository.clear_cart(cart_id)
        self._update_cart_total(cart_id)
        return cleared_count
    
    def _update_cart_total(self, cart_id):
        """Mettre à jour le total du panier"""
        total = self.item_repository.get_cart_total(cart_id)
        return self.cart_repository.update_cart_total(cart_id, total)

    def _validate_user_exists(self, user_id):
        """Valider que l'utilisateur existe via le microservice users"""
        try:
            response = requests.get(f"http://localhost:8000/users/api/v1/customers/{user_id}")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Échec de validation de l'utilisateur {user_id}: {e}")
            return False

    def _get_user_info(self, user_id):
        """Obtenir les informations de l'utilisateur depuis le microservice users"""
        try:
            response = requests.get(f"http://localhost:8000/users/api/v1/customers/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"Échec de récupération des infos utilisateur {user_id}: {e}")
            return None
    
    def _get_product_info(self, product_id):
        """Obtenir les informations du produit depuis le microservice produits"""
        try:
            response = requests.get(f"http://kong-api_gateway:8000/products/api/v1/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"Échec de récupération des infos produit {product_id}: {e}")
            return None
            
    def _check_stock_availability(self, product_id, store_id, quantity):
        """Vérifier la disponibilité du stock depuis le microservice warehouse"""
        try:
            response = requests.get(f"http://kong-api_gateway:8000/warehouse/api/v1/stocks/product/{product_id}/store/{store_id}")
            if response.status_code == 200:
                stock_data = response.json()
                return stock_data['quantite'] >= quantity
            return False
        except Exception as e:
            logging.error(f"Échec de vérification du stock: {e}")
            return False


class CheckoutService:
    def __init__(self, session):
        self.session = session
        self.checkout_repository = CheckoutRepository(session)
        self.cart_service = CartService(session)

    def get_checkout_by_id(self, checkout_id):
        checkout = self.checkout_repository.get_by_id(checkout_id)
        return checkout
    
    def get_checkouts_by_user(self, user_id):
        checkouts = self.checkout_repository.get_by_user_id(user_id)
        return checkouts

    def initiate_checkout(self, cart_id):
        """Initier le processus de checkout avec validation complète"""
        
        cart_data = self.cart_service.get_cart_with_items(cart_id)
        if not cart_data or not cart_data['items']:
            raise ValueError("Le panier est vide ou n'existe pas")
            
        # for item in cart_data['items']:
        #     if not self._check_stock_availability(item, cart_data['cart'].store, quantity=item.quantite):
        #         raise ValueError(f"Stock insuffisant pour le produit {item.product}")
                
        total_amount = cart_data['calculated_total']
        
        checkout = self.checkout_repository.create_checkout(
            cart_id
        )
        
        return checkout
    
    def complete_checkout(self, checkout_id):
        """Finaliser le checkout avec intégration warehouse"""
        checkout = self.checkout_repository.get_by_id(checkout_id)
        if not checkout:
            raise ValueError("Checkout non trouvé")
            
        try:
            
            # 3. Réduire le stock dans le warehouse pour chaque article
            cart_data = self.cart_service.get_cart_with_items(checkout.cart_id)
            cart = cart_data['cart']
            
            for item in cart_data['items']:
                success = self._reduce_warehouse_stock(item.product, cart.store, item.quantite)
                if not success:
                    raise ValueError(f"Échec de réduction du stock pour le produit {item.product}")
            
            # 4. Finaliser le checkout
            completed_checkout = self.checkout_repository.complete_checkout(checkout_id)
            
            # 5. Vider le panier
            self.cart_service.clear_cart(checkout.cart_id)
            
            logging.info(f"Checkout {checkout_id} complété avec succès pour le cart {checkout.cart_id}")
            return completed_checkout
            
        except Exception as e:
            # En cas d'erreur, annuler le checkout et restaurer le stock si nécessaire
            self.checkout_repository.update_checkout_status(checkout_id, "cancelled")
            raise ValueError(f"Échec du checkout: {e}")
    
    def cancel_checkout(self, checkout_id):
        """Annuler un checkout"""
        return self.checkout_repository.update_checkout_status(checkout_id, "cancelled")
    
    def _validate_item_stock(self, item):
        """Valider qu'un article a suffisamment de stock"""
        # Note: On devrait obtenir le store_id du panier
        try:
            response = requests.get(f"http://localhost:8000/warehouse/api/v1/stocks/product/{item.product_id}")
            if response.status_code == 200:
                stocks = response.json()
                total_available = sum(stock['quantite'] for stock in stocks)
                return total_available >= item.quantite
            return False
        except Exception as e:
            logging.error(f"Échec de validation du stock: {e}")
            return False

    def _validate_user_exists(self, user_id):
        """Valider que l'utilisateur existe via le microservice users"""
        try:
            response = requests.get(f"http://localhost:8000/users/api/v1/customers/{user_id}")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Échec de validation de l'utilisateur {user_id}: {e}")
            return False

    def _check_stock_availability(self, product_id, store_id, quantity):
        """Vérifier la disponibilité du stock depuis le microservice warehouse"""
        try:
            response = requests.get(f"http://kong-api_gateway:8000/warehouse/api/v1/stocks/product/{product_id}/store/{store_id}")
            if response.status_code == 200:
                stock_data = response.json()
                return stock_data['quantite'] >= quantity
            return False
        except Exception as e:
            logging.error(f"Échec de vérification du stock: {e}")
            return False
    
    def _reduce_warehouse_stock(self, product_id, store_id, quantity):
        """Réduire le stock dans le microservice warehouse"""
        try:
            response = requests.post(
                f"http://kong-api_gateway:8000/warehouse/api/v1/stocks/reduce",
                params={
                    "product": product_id,
                    "store": store_id,
                    "quantity": quantity
                }
            )
            if response.status_code != 200:
                logging.error(f"Échec de réduction du stock: {response.text}")
                return False
            return True
        except Exception as e:
            logging.error(f"Échec de réduction du stock: {e}")
            return False

    def _get_user_info(self, user_id):
        """Obtenir les informations de l'utilisateur depuis le microservice users"""
        try:
            response = requests.get(f"http://kong-api_gateway:8000/users/api/v1/customers/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"Échec de récupération des infos utilisateur {user_id}: {e}")
            return None
