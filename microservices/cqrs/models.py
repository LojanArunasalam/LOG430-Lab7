# CQRS with Event Broker Implementation

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# COMMAND SIDE - Write Model
# ============================================================================

class Command(ABC):
    """Base command class"""
    def __init__(self, command_id: str = None):
        self.command_id = command_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow()

class CreateOrderCommand(Command):
    def __init__(self, user_id: int, product_id: int, quantity: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

class ProcessPaymentCommand(Command):
    def __init__(self, order_id: str, amount: float, payment_method: str, **kwargs):
        super().__init__(**kwargs)
        self.order_id = order_id
        self.amount = amount
        self.payment_method = payment_method

class UpdateInventoryCommand(Command):
    def __init__(self, product_id: int, quantity_change: int, operation: str, **kwargs):
        super().__init__(**kwargs)
        self.product_id = product_id
        self.quantity_change = quantity_change
        self.operation = operation  # 'reserve', 'release', 'deduct'

# ============================================================================
# QUERY SIDE - Read Model
# ============================================================================

class Query(ABC):
    """Base query class"""
    def __init__(self, query_id: str = None):
        self.query_id = query_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow()

class GetOrderQuery(Query):
    def __init__(self, order_id: str, **kwargs):
        super().__init__(**kwargs)
        self.order_id = order_id

class GetUserOrdersQuery(Query):
    def __init__(self, user_id: int, status: str = None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.status = status

class GetInventoryQuery(Query):
    def __init__(self, product_id: int = None, **kwargs):
        super().__init__(**kwargs)
        self.product_id = product_id

class GetOrderStatisticsQuery(Query):
    def __init__(self, start_date: datetime = None, end_date: datetime = None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

# ============================================================================
# READ MODELS - Optimized for Queries
# ============================================================================

class OrderReadModel:
    """Optimized read model for order queries"""
    def __init__(self):
        self.order_id: str = ""
        self.user_id: int = 0
        self.user_email: str = ""
        self.user_name: str = ""
        self.total_amount: float = 0.0
        self.status: str = ""
        self.created_at: datetime = None
        self.updated_at: datetime = None
        self.items: List[Dict] = []
        self.payment_info: Dict = {}
        self.shipping_info: Dict = {}
        self.timeline: List[Dict] = []  # Event timeline for order

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_name": self.user_name,
            "total_amount": self.total_amount,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "items": self.items,
            "payment_info": self.payment_info,
            "shipping_info": self.shipping_info,
            "timeline": self.timeline
        }

class InventoryReadModel:
    """Optimized read model for inventory queries"""
    def __init__(self):
        self.product_id: int = 0
        self.product_name: str = ""
        self.available_quantity: int = 0
        self.reserved_quantity: int = 0
        self.total_quantity: int = 0
        self.reorder_level: int = 0
        self.last_restocked: datetime = None
        self.pending_orders: List[Dict] = []
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "available_quantity": self.available_quantity,
            "reserved_quantity": self.reserved_quantity,
            "total_quantity": self.total_quantity,
            "reorder_level": self.reorder_level,
            "last_restocked": self.last_restocked.isoformat() if self.last_restocked else None,
            "pending_orders": self.pending_orders,
            "low_stock_alert": self.available_quantity <= self.reorder_level
        }

class UserOrderSummaryReadModel:
    """Optimized read model for user order summaries"""
    def __init__(self):
        self.user_id: int = 0
        self.user_email: str = ""
        self.total_orders: int = 0
        self.total_spent: float = 0.0
        self.avg_order_value: float = 0.0
        self.last_order_date: datetime = None
        self.favorite_products: List[Dict] = []
        self.order_statuses: Dict[str, int] = {}
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "user_email": self.user_email,
            "total_orders": self.total_orders,
            "total_spent": self.total_spent,
            "avg_order_value": self.avg_order_value,
            "last_order_date": self.last_order_date.isoformat() if self.last_order_date else None,
            "favorite_products": self.favorite_products,
            "order_statuses": self.order_statuses
        }

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

class CommandHandler(ABC):
    """Base command handler"""
    
    @abstractmethod
    async def handle(self, command: Command) -> Dict[str, Any]:
        pass

class CreateOrderCommandHandler(CommandHandler):
    def __init__(self, event_publisher):
        self.event_publisher = event_publisher
        
    async def handle(self, command: CreateOrderCommand) -> Dict[str, Any]:
        """Handle create order command"""
        try:
            # Generate order ID
            order_id = str(uuid.uuid4())
            
            # Publish OrderInitiated event
            event_data = {
                "order_id": order_id,
                "user_id": command.user_id,
                "product_id": command.product_id,
                "quantity": command.quantity,
                "command_id": command.command_id
            }
            
            self.event_publisher.publish_event(
                event_type="OrderInitiated",
                aggregate_type="orders",
                aggregate_id=order_id,
                data=event_data,
                service_name="cqrs-command"
            )
            
            logger.info(f"Order command processed: {order_id}")
            
            return {
                "success": True,
                "order_id": order_id,
                "command_id": command.command_id,
                "message": "Order creation initiated"
            }
            
        except Exception as e:
            logger.error(f"Error handling CreateOrderCommand: {e}")
            return {
                "success": False,
                "error": str(e),
                "command_id": command.command_id
            }

class ProcessPaymentCommandHandler(CommandHandler):
    def __init__(self, event_publisher):
        self.event_publisher = event_publisher
        
    async def handle(self, command: ProcessPaymentCommand) -> Dict[str, Any]:
        """Handle process payment command"""
        try:
            # Generate payment ID
            payment_id = str(uuid.uuid4())
            
            # Publish PaymentInitiated event
            event_data = {
                "payment_id": payment_id,
                "order_id": command.order_id,
                "amount": command.amount,
                "payment_method": command.payment_method,
                "command_id": command.command_id
            }
            
            self.event_publisher.publish_event(
                event_type="PaymentInitiated",
                aggregate_type="payments",
                aggregate_id=payment_id,
                data=event_data,
                service_name="cqrs-command"
            )
            
            logger.info(f"Payment command processed: {payment_id}")
            
            return {
                "success": True,
                "payment_id": payment_id,
                "order_id": command.order_id,
                "command_id": command.command_id,
                "message": "Payment processing initiated"
            }
            
        except Exception as e:
            logger.error(f"Error handling ProcessPaymentCommand: {e}")
            return {
                "success": False,
                "error": str(e),
                "command_id": command.command_id
            }

# ============================================================================
# QUERY HANDLERS
# ============================================================================

class QueryHandler(ABC):
    """Base query handler"""
    
    @abstractmethod
    async def handle(self, query: Query) -> Dict[str, Any]:
        pass

class GetOrderQueryHandler(QueryHandler):
    def __init__(self, read_store):
        self.read_store = read_store
        
    async def handle(self, query: GetOrderQuery) -> Dict[str, Any]:
        """Handle get order query"""
        try:
            order = await self.read_store.get_order(query.order_id)
            
            if order:
                return {
                    "success": True,
                    "data": order.to_dict(),
                    "query_id": query.query_id
                }
            else:
                return {
                    "success": False,
                    "error": "Order not found",
                    "query_id": query.query_id
                }
                
        except Exception as e:
            logger.error(f"Error handling GetOrderQuery: {e}")
            return {
                "success": False,
                "error": str(e),
                "query_id": query.query_id
            }

class GetUserOrdersQueryHandler(QueryHandler):
    def __init__(self, read_store):
        self.read_store = read_store
        
    async def handle(self, query: GetUserOrdersQuery) -> Dict[str, Any]:
        """Handle get user orders query"""
        try:
            orders = await self.read_store.get_user_orders(query.user_id, query.status)
            
            return {
                "success": True,
                "data": [order.to_dict() for order in orders],
                "count": len(orders),
                "query_id": query.query_id
            }
                
        except Exception as e:
            logger.error(f"Error handling GetUserOrdersQuery: {e}")
            return {
                "success": False,
                "error": str(e),
                "query_id": query.query_id
            }

class GetInventoryQueryHandler(QueryHandler):
    def __init__(self, read_store):
        self.read_store = read_store
        
    async def handle(self, query: GetInventoryQuery) -> Dict[str, Any]:
        """Handle get inventory query"""
        try:
            if query.product_id:
                inventory = await self.read_store.get_product_inventory(query.product_id)
                data = inventory.to_dict() if inventory else None
            else:
                inventories = await self.read_store.get_all_inventory()
                data = [inv.to_dict() for inv in inventories]
            
            return {
                "success": True,
                "data": data,
                "query_id": query.query_id
            }
                
        except Exception as e:
            logger.error(f"Error handling GetInventoryQuery: {e}")
            return {
                "success": False,
                "error": str(e),
                "query_id": query.query_id
            }
