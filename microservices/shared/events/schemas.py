# Event Schemas and Definitions

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class BaseEvent:
    """Base event class with common fields"""
    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    version: int
    timestamp: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]

# Order Events
class OrderEvents:
    ORDER_INITIATED = "OrderInitiated"
    ORDER_CREATED = "OrderCreated"
    ORDER_CONFIRMED = "OrderConfirmed"
    ORDER_CANCELLED = "OrderCancelled"
    ORDER_COMPLETED = "OrderCompleted"

# Inventory Events
class InventoryEvents:
    STOCK_CHECKED = "StockChecked"
    STOCK_RESERVED = "StockReserved"
    STOCK_RELEASED = "StockReleased"
    STOCK_DEDUCTED = "StockDeducted"
    STOCK_UNAVAILABLE = "StockUnavailable"

# Payment Events
class PaymentEvents:
    PAYMENT_INITIATED = "PaymentInitiated"
    PAYMENT_PROCESSED = "PaymentProcessed"
    PAYMENT_FAILED = "PaymentFailed"
    PAYMENT_REFUNDED = "PaymentRefunded"

# Shipping Events
class ShippingEvents:
    SHIPMENT_PREPARED = "ShipmentPrepared"
    SHIPMENT_DISPATCHED = "ShipmentDispatched"
    SHIPMENT_DELIVERED = "ShipmentDelivered"
    SHIPMENT_FAILED = "ShipmentFailed"

# Notification Events
class NotificationEvents:
    ORDER_CONFIRMATION_SENT = "OrderConfirmationSent"
    SHIPPING_NOTIFICATION_SENT = "ShippingNotificationSent"
    DELIVERY_NOTIFICATION_SENT = "DeliveryNotificationSent"

# Aggregate Types
class AggregateTypes:
    ORDER = "orders"
    INVENTORY = "inventory"
    PAYMENT = "payments"
    SHIPMENT = "shipping"
    NOTIFICATION = "notifications"
    ANALYTICS = "analytics"

# Exchange Names
class Exchanges:
    ORDERS = "ecommerce.orders"
    INVENTORY = "ecommerce.inventory"
    PAYMENTS = "ecommerce.payments"
    SHIPPING = "ecommerce.shipping"
    NOTIFICATIONS = "ecommerce.notifications"
    ANALYTICS = "ecommerce.analytics"

# Routing Keys
class RoutingKeys:
    # Order routing keys
    ORDER_INITIATED = "orders.order_initiated"
    ORDER_CREATED = "orders.order_created"
    ORDER_CONFIRMED = "orders.order_confirmed"
    ORDER_CANCELLED = "orders.order_cancelled"
    
    # Inventory routing keys
    STOCK_CHECKED = "inventory.stock_checked"
    STOCK_RESERVED = "inventory.stock_reserved"
    STOCK_RELEASED = "inventory.stock_released"
    STOCK_UNAVAILABLE = "inventory.stock_unavailable"
    
    # Payment routing keys
    PAYMENT_PROCESSED = "payments.payment_processed"
    PAYMENT_FAILED = "payments.payment_failed"
    
    # Shipping routing keys
    SHIPMENT_PREPARED = "shipping.shipment_prepared"
    SHIPMENT_DISPATCHED = "shipping.shipment_dispatched"
    
    # Notification routing keys
    CONFIRMATION_SENT = "notifications.order_confirmation_sent"
    SHIPPING_SENT = "notifications.shipping_notification_sent"

def create_order_initiated_data(order_id: int, customer_id: int, cart_id: int, total_amount: float, items: list) -> Dict[str, Any]:
    """Helper to create OrderInitiated event data"""
    return {
        "order_id": order_id,
        "customer_id": customer_id,
        "cart_id": cart_id,
        "total_amount": total_amount,
        "status": "INITIATED",
        "items": items,
        "created_at": datetime.utcnow().isoformat()
    }

def create_stock_reserved_data(order_id: int, store_id: int, items: list, reservation_id: str = None) -> Dict[str, Any]:
    """Helper to create StockReserved event data"""
    return {
        "order_id": order_id,
        "store_id": store_id,
        "reservation_id": reservation_id or f"res_{order_id}_{datetime.utcnow().timestamp()}",
        "items": items,
        "reserved_at": datetime.utcnow().isoformat()
    }

def create_payment_processed_data(order_id: int, payment_id: str, amount: float, currency: str = "CAD") -> Dict[str, Any]:
    """Helper to create PaymentProcessed event data"""
    return {
        "order_id": order_id,
        "payment_id": payment_id,
        "amount": amount,
        "currency": currency,
        "status": "PROCESSED",
        "processed_at": datetime.utcnow().isoformat()
    }
