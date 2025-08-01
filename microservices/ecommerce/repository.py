import logging
from models.cart_model import Cart
from models.item_cart_model import ItemCart
from models.checkout_model import Checkout

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

class CartRepository:
    def __init__(self, session):
        self.session = session
        self.session.expire_on_commit = False  # Prevent session from expiring on commit


    def get_by_id(self, cart_id):
        logging.debug(f"Fetching cart with id {cart_id}")
        cart = self.session.query(Cart).filter_by(id=cart_id).first()
        if not cart:
            logging.warning(f"No cart found with id {cart_id}")
            return None
        logging.debug(f"Fetched successfully cart with id {cart_id}")
        return cart
    
    def get_by_user_id(self, user_id):
        logging.debug(f"Fetching cart for user {user_id}")
        cart = self.session.query(Cart).filter_by(user=user_id).first()
        if not cart:
            logging.warning(f"No cart found for user {user_id}")
            return None
        logging.debug(f"Fetched successfully cart for user {user_id}")
        return cart
    
    def get_by_user_and_store(self, user_id, store_id):
        logging.debug(f"Fetching cart for user {user_id} in store {store_id}")
        cart = self.session.query(Cart).filter_by(user=user_id, store=store_id).first()
        if not cart:
            logging.warning(f"No cart found for user {user_id} in store {store_id}")
            return None
        logging.debug(f"Fetched successfully cart for user {user_id} in store {store_id}")
        return cart
    
    def get_all_carts(self):
        logging.debug("Fetching all carts")
        carts = self.session.query(Cart).all()
        if not carts:
            logging.warning("No carts found")
            return None
        logging.debug(f"Fetched successfully {len(carts)} carts")
        return carts
    
    def create_cart(self, user_id, store_id):
        logging.debug(f"Creating cart for user {user_id} in store {store_id}")
        cart = Cart(user=user_id, store=store_id, total=0.0)
        self.session.add(cart)
        self.session.commit()
        logging.debug(f"Cart created successfully with id {cart.id}")
        return cart
        
    def update_cart_total(self, cart_id, new_total):
        logging.debug(f"Updating cart {cart_id} total to {new_total}")
        cart = self.get_by_id(cart_id)
        if not cart:
            logging.error(f"Cart with id {cart_id} does not exist")
            return None
        cart.total_price = new_total
        self.session.commit()
        logging.debug(f"Cart {cart_id} total updated successfully")
        return cart
        
    def delete_cart(self, cart_id):
        logging.debug(f"Deleting cart with id {cart_id}")
        cart = self.get_by_id(cart_id)
        if not cart:
            logging.error(f"Cart with id {cart_id} does not exist")
            return None
        self.session.delete(cart)
        self.session.commit()
        logging.debug(f"Cart with id {cart_id} deleted successfully")
        return cart


class ItemCartRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, item_id):
        logging.debug(f"Fetching cart item with id {item_id}")
        item = self.session.query(ItemCart).filter_by(id=item_id).first()
        if not item:
            logging.warning(f"No cart item found with id {item_id}")
            return None
        logging.debug(f"Fetched successfully cart item with id {item_id}")
        return item
    
    def get_items_by_cart_id(self, cart_id):
        logging.debug(f"Fetching all items for cart {cart_id}")
        items = self.session.query(ItemCart).filter_by(cart=cart_id).all()
        if not items:
            logging.warning(f"No items found for cart {cart_id}")
            return []
        logging.debug(f"Fetched successfully {len(items)} items for cart {cart_id}")
        return items
    
    def get_item_by_cart_and_product(self, cart_id, product_id):
        logging.debug(f"Fetching item for cart {cart_id} and product {product_id}")
        item = self.session.query(ItemCart).filter_by(cart=cart_id, product=product_id).first()
        if not item:
            logging.warning(f"No item found for cart {cart_id} and product {product_id}")
            return None
        logging.debug(f"Fetched successfully item for cart {cart_id} and product {product_id}")
        return item
    
    def add_item_to_cart(self, cart_id, product_id, quantity, price):
        logging.debug(f"Adding item to cart {cart_id}: product {product_id}, quantity {quantity}")
        
        # Check if item already exists in cart
        existing_item = self.get_item_by_cart_and_product(cart_id, product_id)
        
        if existing_item:
            # Update existing item quantity
            existing_item.quantite += quantity
            existing_item.prix = price * existing_item.quantite
            self.session.commit()
            logging.debug(f"Updated existing item quantity to {existing_item.quantite}")
            return existing_item
        else:
            # Create new item
            item = ItemCart(
                cart=cart_id,
                product=product_id,
                quantite=quantity,
                prix=price * quantity
            )
            self.session.add(item)
            self.session.commit()
            logging.debug(f"Added new item to cart with id {item.id}")
            return item
    
    def update_item_quantity(self, item_id, new_quantity, unit_price):
        logging.debug(f"Updating item {item_id} quantity to {new_quantity}")
        item = self.get_by_id(item_id)
        if not item:
            logging.error(f"Item with id {item_id} does not exist")
            return None
        
        if new_quantity <= 0:
            # Remove item if quantity is 0 or negative
            return self.remove_item_from_cart(item_id)
        
        item.quantite = new_quantity
        item.prix = unit_price * new_quantity
        self.session.commit()
        logging.debug(f"Item {item_id} quantity updated successfully")
        return item
    
    def remove_item_from_cart(self, item_id):
        logging.debug(f"Removing item {item_id} from cart")
        item = self.get_by_id(item_id)
        if not item:
            logging.error(f"Item with id {item_id} does not exist")
            return None
        
        cart_id = item.sale_id
        self.session.delete(item)
        self.session.commit()
        logging.debug(f"Item {item_id} removed from cart {cart_id}")
        return item
    
    def clear_cart(self, cart_id):
        logging.debug(f"Clearing all items from cart {cart_id}")
        items = self.get_items_by_cart_id(cart_id)
        for item in items:
            self.session.delete(item)
        self.session.commit()
        logging.debug(f"Cleared {len(items)} items from cart {cart_id}")
        return len(items)
    
    def get_cart_total(self, cart_id):
        logging.debug(f"Calculating total for cart {cart_id}")
        items = self.get_items_by_cart_id(cart_id)
        total = sum(item.prix for item in items)
        logging.debug(f"Cart {cart_id} total: {total}")
        return total


class CheckoutRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, checkout_id):
        logging.debug(f"Fetching checkout with id {checkout_id}")
        checkout = self.session.query(Checkout).filter_by(id=checkout_id).first()
        if not checkout:
            logging.warning(f"No checkout found with id {checkout_id}")
            return None
        logging.debug(f"Fetched successfully checkout with id {checkout_id}")
        return checkout
    
    def get_by_cart_id(self, cart_id):
        logging.debug(f"Fetching checkout for cart {cart_id}")
        checkout = self.session.query(Checkout).filter_by(cart_id=cart_id).first()
        if not checkout:
            logging.warning(f"No checkout found for cart {cart_id}")
            return None
        logging.debug(f"Fetched successfully checkout for cart {cart_id}")
        return checkout
    
    def get_by_user_id(self, user_id):
        logging.debug(f"Fetching checkouts for user {user_id}")
        checkouts = self.session.query(Checkout).filter_by(user=user_id).all()
        if not checkouts:
            logging.warning(f"No checkouts found for user {user_id}")
            return []
        logging.debug(f"Fetched successfully {len(checkouts)} checkouts for user {user_id}")
        return checkouts
    
    def create_checkout(self, cart_id):
        logging.debug(f"Creating checkout for cart {cart_id}")
        checkout = Checkout(
            cart_id=cart_id
        )
        self.session.add(checkout)
        self.session.commit()
        logging.debug(f"Checkout created successfully with id {checkout.id}")
        return checkout
    
    def update_checkout_status(self, checkout_id, new_status):
        logging.debug(f"Updating checkout {checkout_id} status to {new_status}")
        checkout = self.get_by_id(checkout_id)
        if not checkout:
            logging.error(f"Checkout with id {checkout_id} does not exist")
            return None
        checkout.status = new_status
        self.session.commit()
        logging.debug(f"Checkout {checkout_id} status updated successfully")
        return checkout
    
    def complete_checkout(self, checkout_id):
        logging.debug(f"Completing checkout {checkout_id}")
        checkout = self.get_by_id(checkout_id)
        if not checkout:
            logging.error(f"Checkout with id {checkout_id} does not exist")
            return None
        checkout.current_status = "completed"
        self.session.commit()
        logging.debug(f"Checkout {checkout_id} completed successfully")
        return checkout


# # Composite Repository for complex operations
# class EcommerceRepository:
#     def __init__(self, session):
#         self.session = session
#         self.cart_repo = CartRepository(session)
#         self.item_repo = ItemCartRepository(session)
#         self.checkout_repo = CheckoutRepository(session)
    
#     def get_cart_with_items(self, cart_id):
#         """Get cart with all its items"""
#         cart = self.cart_repo.get_by_id(cart_id)
#         if not cart:
#             return None
        
#         items = self.item_repo.get_items_by_cart_id(cart_id)
#         return {
#             'cart': cart,
#             'items': items,
#             'item_count': len(items),
#             'calculated_total': sum(item.prix for item in items)
#         }
    
#     def update_cart_totals(self, cart_id):
#         """Recalculate and update cart total based on items"""
#         total = self.item_repo.get_cart_total(cart_id)
#         return self.cart_repo.update_cart_total(cart_id, total)
    
#     def transfer_cart_to_checkout(self, cart_id, user_id, shipping_info):
#         """Create checkout from cart and clear cart"""
#         # Get cart total
#         total = self.item_repo.get_cart_total(cart_id)
        
#         # Create checkout
#         checkout = self.checkout_repo.create_checkout(cart_id, user_id, shipping_info, total)
        
#         return checkout