from fastapi import FastAPI, HTTPException, Depends
from service import CartService, CheckoutService
from models.cart_model import Cart
from models.item_cart_model import ItemCart
from models.checkout_model import Checkout
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
import os
import sys
import logging
from dotenv import load_dotenv

# Add shared directory to path
sys.path.append('/app/../shared')
from events import (
    EventPublisher, 
    OrderEvents, 
    AggregateTypes,
    create_order_initiated_data
)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ecommerce API")

# Database setup
DATABASE_URL_ECOMMERCE = os.getenv("DATABASE_URL_ECOMMERCE")
engine = create_engine(DATABASE_URL_ECOMMERCE)
Session = sessionmaker(bind=engine)

# Event publisher (initialized once)
event_publisher = None

def get_event_publisher():
    """Get or create event publisher instance"""
    global event_publisher
    if event_publisher is None:
        try:
            event_publisher = EventPublisher()
            logger.info("Event publisher initialized")
        except Exception as e:
            logger.error(f"Failed to initialize event publisher: {e}")
            event_publisher = None
    return event_publisher

# Pydantic Models for Request/Response
class CartSerializer(BaseModel):
    id: int
    user: int
    total: float
    store: int

class ItemCartSerializer(BaseModel):
    id: int
    quantite: int
    cart: int 
    product: int
    

class CartCreateSerializer(BaseModel):
    user: int
    store: int

class AddItemToCartSerializer(BaseModel):
    quantite: int
    cart: int  
    product: int 
    store_id: int
    

class UpdateItemSerializer(BaseModel):
    quantity: int

class CheckoutSerializer(BaseModel):
    id: int
    cart_id: int

class CheckoutCreateSerializer(BaseModel):
    cart_id: int

class CompleteCheckoutSerializer(BaseModel):
    payment_method: str
    payment_reference: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ecommerce API"}

# Cart Endpoints
@app.post("/api/v1/cart/add-item", response_model=ItemCartSerializer)
def add_item_to_cart(item_data: AddItemToCartSerializer):
    """Add item to user's cart"""
    session = Session()
    cart_service = CartService(session)
    item = cart_service.add_item_to_cart(
        item_data.cart, 
        item_data.product, 
        item_data.quantite,
        item_data.store_id
    )
    return item

@app.get("/api/v1/cart/user/{user_id}", response_model=CartSerializer)
def get_user_cart(user_id: int):
    """Get user's active cart"""
    session = Session()
    cart_service = CartService(session)
    cart = cart_service.get_cart_by_user(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@app.get("/api/v1/cart/{cart_id}/details")
def get_cart_with_items(cart_id: int):
    """Get cart with all items and details"""
    session = Session()
    cart_service = CartService(session)
    cart_data = cart_service.get_cart_with_items(cart_id)
    if not cart_data:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart_data

@app.get("/api/v1/cart/{cart_id}/items", response_model=List[ItemCartSerializer])
def get_cart_items(cart_id: int):
    """Get all items in a cart"""
    session = Session()
    cart_service = CartService(session)
    cart_data = cart_service.get_cart_with_items(cart_id)
    if not cart_data:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart_data['items']

@app.put("/api/v1/cart/item/{item_id}", response_model=ItemCartSerializer)
def update_cart_item(item_id: int, update_data: UpdateItemSerializer):
    """Update cart item quantity"""
    session = Session()
    cart_service = CartService(session)
    updated_item = cart_service.update_item_quantity(item_id, update_data.quantity)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@app.delete("/api/v1/cart/item/{item_id}")
def remove_cart_item(item_id: int):
    """Remove item from cart"""
    session = Session()
    cart_service = CartService(session)
    removed_item = cart_service.remove_item_from_cart(item_id)
    if not removed_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item removed from cart successfully"}

@app.delete("/api/v1/cart/{cart_id}/clear")
def clear_cart(cart_id: int):
    """Clear all items from cart"""
    session = Session()
    cart_service = CartService(session)
    cleared_count = cart_service.clear_cart(cart_id)
    return {
        "detail": f"Cart cleared successfully", 
        "items_removed": cleared_count
    }

# Checkout Endpoints
@app.post("/api/v1/checkout/initiate", response_model=CheckoutSerializer)
def initiate_checkout(checkout_data: CheckoutCreateSerializer):
    """Start checkout process"""
    session = Session()
    checkout_service = CheckoutService(session)
    
    checkout = checkout_service.initiate_checkout(
        checkout_data.cart_id
    )
    
    # Publish OrderInitiated event
    publisher = get_event_publisher()
    if publisher:
        try:
            # Get cart items for the event
            cart_service = CartService(session)
            cart_data = cart_service.get_cart_with_items(checkout_data.cart_id)
            
            items_data = []
            if cart_data and 'items' in cart_data:
                for item in cart_data['items']:
                    items_data.append({
                        "product_id": item.get('product', 0),
                        "quantity": item.get('quantite', 0),
                        "unit_price": 25.99,  # Default price - you'd get this from products service
                        "total_price": item.get('quantite', 0) * 25.99
                    })
            
            event_data = create_order_initiated_data(
                order_id=checkout.id,
                customer_id=checkout.customer_id,
                cart_id=checkout_data.cart_id,
                total_amount=float(checkout.total),
                items=items_data
            )
            
            publisher.publish_event(
                event_type=OrderEvents.ORDER_INITIATED,
                aggregate_type=AggregateTypes.ORDER,
                aggregate_id=str(checkout.id),
                data=event_data,
                service_name="ecommerce"
            )
            
            logger.info(f"Published OrderInitiated event for checkout {checkout.id}")
            
        except Exception as e:
            logger.error(f"Failed to publish OrderInitiated event: {e}")
            # Don't fail the checkout if event publishing fails
    
    return checkout

@app.post("/api/v1/checkout/{checkout_id}/complete", response_model=CheckoutSerializer)
def complete_checkout(checkout_id: int):
    session = Session()
    checkout_service = CheckoutService(session)
    
    completed_checkout = checkout_service.complete_checkout(checkout_id)
    
    # Publish OrderCreated event
    publisher = get_event_publisher()
    if publisher:
        try:
            event_data = {
                "order_id": checkout_id,
                "customer_id": completed_checkout.customer_id,
                "total_amount": float(completed_checkout.total),
                "status": "CREATED",
                "completed_at": completed_checkout.created_at.isoformat() if completed_checkout.created_at else None
            }
            
            publisher.publish_event(
                event_type=OrderEvents.ORDER_CREATED,
                aggregate_type=AggregateTypes.ORDER,
                aggregate_id=str(checkout_id),
                data=event_data,
                service_name="ecommerce"
            )
            
            logger.info(f"Published OrderCreated event for order {checkout_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish OrderCreated event: {e}")
    
    return completed_checkout

@app.get("/api/v1/checkout/{checkout_id}", response_model=CheckoutSerializer)
def get_checkout(checkout_id: int):
    """Get checkout details"""
    session = Session()
    checkout_service = CheckoutService(session)
    checkout = checkout_service.get_checkout_by_id(checkout_id)
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout not found")
    return checkout

@app.put("/api/v1/checkout/{checkout_id}/cancel")
def cancel_checkout(checkout_id: int):
    """Cancel a checkout"""
    session = Session()
    checkout_service = CheckoutService(session)
    cancelled_checkout = checkout_service.cancel_checkout(checkout_id)
    if not cancelled_checkout:
        raise HTTPException(status_code=404, detail="Checkout not found")
    return {"detail": "Checkout cancelled successfully"}