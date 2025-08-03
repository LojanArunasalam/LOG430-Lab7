# CQRS Event Projectors - Update Read Models from Events

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from ..shared.events.subscriber import EventSubscriber
from .read_store import CQRSReadStore
from .models import OrderReadModel, InventoryReadModel, UserOrderSummaryReadModel

logger = logging.getLogger(__name__)

class EventProjector:
    """Base class for event projectors that update read models"""
    
    def __init__(self, read_store: CQRSReadStore):
        self.read_store = read_store
    
    async def project_event(self, event: Dict[str, Any]):
        """Project an event to update read models"""
        event_type = event.get("event_type")
        
        if hasattr(self, f"handle_{event_type.lower()}"):
            handler = getattr(self, f"handle_{event_type.lower()}")
            await handler(event)
        else:
            logger.debug(f"No handler for event type: {event_type}")

class OrderProjector(EventProjector):
    """Projector for order-related events"""
    
    async def handle_orderinitiated(self, event: Dict[str, Any]):
        """Handle OrderInitiated event"""
        try:
            data = event.get("data", {})
            
            # Create new order read model
            order = OrderReadModel()
            order.order_id = data.get("order_id")
            order.user_id = data.get("user_id")
            order.status = "INITIATED"
            order.created_at = datetime.fromisoformat(event.get("timestamp"))
            order.updated_at = order.created_at
            
            # Add to timeline
            order.timeline.append({
                "event": "OrderInitiated",
                "timestamp": order.created_at.isoformat(),
                "data": data
            })
            
            # Add order items
            order.items = [{
                "product_id": data.get("product_id"),
                "quantity": data.get("quantity"),
                "status": "PENDING"
            }]
            
            await self.read_store.upsert_order(order)
            logger.info(f"Projected OrderInitiated: {order.order_id}")
            
        except Exception as e:
            logger.error(f"Error projecting OrderInitiated: {e}")
    
    async def handle_ordervalidated(self, event: Dict[str, Any]):
        """Handle OrderValidated event"""
        try:
            data = event.get("data", {})
            order_id = data.get("order_id")
            
            # Get existing order
            order = await self.read_store.get_order(order_id)
            if not order:
                logger.warning(f"Order not found for OrderValidated: {order_id}")
                return
            
            # Update order status
            order.status = "VALIDATED"
            order.updated_at = datetime.fromisoformat(event.get("timestamp"))
            order.total_amount = data.get("total_amount", 0.0)
            
            # Update timeline
            order.timeline.append({
                "event": "OrderValidated",
                "timestamp": order.updated_at.isoformat(),
                "data": data
            })
            
            await self.read_store.upsert_order(order)
            logger.info(f"Projected OrderValidated: {order_id}")
            
        except Exception as e:
            logger.error(f"Error projecting OrderValidated: {e}")
    
    async def handle_orderpaid(self, event: Dict[str, Any]):
        """Handle OrderPaid event"""
        try:
            data = event.get("data", {})
            order_id = data.get("order_id")
            
            # Get existing order
            order = await self.read_store.get_order(order_id)
            if not order:
                logger.warning(f"Order not found for OrderPaid: {order_id}")
                return
            
            # Update order status and payment info
            order.status = "PAID"
            order.updated_at = datetime.fromisoformat(event.get("timestamp"))
            order.payment_info = {
                "payment_id": data.get("payment_id"),
                "amount": data.get("amount"),
                "payment_method": data.get("payment_method", ""),
                "processed_at": order.updated_at.isoformat()
            }
            
            # Update timeline
            order.timeline.append({
                "event": "OrderPaid",
                "timestamp": order.updated_at.isoformat(),
                "data": data
            })
            
            await self.read_store.upsert_order(order)
            logger.info(f"Projected OrderPaid: {order_id}")
            
        except Exception as e:
            logger.error(f"Error projecting OrderPaid: {e}")
    
    async def handle_ordershipped(self, event: Dict[str, Any]):
        """Handle OrderShipped event"""
        try:
            data = event.get("data", {})
            order_id = data.get("order_id")
            
            # Get existing order
            order = await self.read_store.get_order(order_id)
            if not order:
                logger.warning(f"Order not found for OrderShipped: {order_id}")
                return
            
            # Update order status and shipping info
            order.status = "SHIPPED"
            order.updated_at = datetime.fromisoformat(event.get("timestamp"))
            order.shipping_info = {
                "tracking_number": data.get("tracking_number", ""),
                "carrier": data.get("carrier", ""),
                "shipped_at": order.updated_at.isoformat(),
                "estimated_delivery": data.get("estimated_delivery", "")
            }
            
            # Update timeline
            order.timeline.append({
                "event": "OrderShipped",
                "timestamp": order.updated_at.isoformat(),
                "data": data
            })
            
            await self.read_store.upsert_order(order)
            logger.info(f"Projected OrderShipped: {order_id}")
            
        except Exception as e:
            logger.error(f"Error projecting OrderShipped: {e}")
    
    async def handle_orderfailed(self, event: Dict[str, Any]):
        """Handle OrderFailed event"""
        try:
            data = event.get("data", {})
            order_id = data.get("order_id")
            
            # Get existing order
            order = await self.read_store.get_order(order_id)
            if not order:
                logger.warning(f"Order not found for OrderFailed: {order_id}")
                return
            
            # Update order status
            order.status = "FAILED"
            order.updated_at = datetime.fromisoformat(event.get("timestamp"))
            
            # Update timeline with failure reason
            order.timeline.append({
                "event": "OrderFailed",
                "timestamp": order.updated_at.isoformat(),
                "data": data,
                "reason": data.get("reason", "Unknown error")
            })
            
            await self.read_store.upsert_order(order)
            logger.info(f"Projected OrderFailed: {order_id}")
            
        except Exception as e:
            logger.error(f"Error projecting OrderFailed: {e}")

class InventoryProjector(EventProjector):
    """Projector for inventory-related events"""
    
    async def handle_inventoryreserved(self, event: Dict[str, Any]):
        """Handle InventoryReserved event"""
        try:
            data = event.get("data", {})
            product_id = data.get("product_id")
            quantity = data.get("quantity", 0)
            
            # Get existing inventory
            inventory = await self.read_store.get_product_inventory(product_id)
            if not inventory:
                # Create new inventory record
                inventory = InventoryReadModel()
                inventory.product_id = product_id
                inventory.product_name = data.get("product_name", f"Product {product_id}")
                inventory.total_quantity = data.get("total_quantity", quantity)
                inventory.reorder_level = data.get("reorder_level", 10)
            
            # Update quantities
            inventory.reserved_quantity += quantity
            inventory.available_quantity = inventory.total_quantity - inventory.reserved_quantity
            
            # Add to pending orders
            inventory.pending_orders.append({
                "order_id": data.get("order_id"),
                "quantity": quantity,
                "reserved_at": event.get("timestamp")
            })
            
            await self.read_store.upsert_inventory(inventory)
            logger.info(f"Projected InventoryReserved: {product_id}, quantity: {quantity}")
            
        except Exception as e:
            logger.error(f"Error projecting InventoryReserved: {e}")
    
    async def handle_inventoryconfirmed(self, event: Dict[str, Any]):
        """Handle InventoryConfirmed event"""
        try:
            data = event.get("data", {})
            product_id = data.get("product_id")
            quantity = data.get("quantity", 0)
            order_id = data.get("order_id")
            
            # Get existing inventory
            inventory = await self.read_store.get_product_inventory(product_id)
            if not inventory:
                logger.warning(f"Inventory not found for InventoryConfirmed: {product_id}")
                return
            
            # Confirm reservation (deduct from total and reserved)
            inventory.total_quantity -= quantity
            inventory.reserved_quantity -= quantity
            inventory.available_quantity = inventory.total_quantity - inventory.reserved_quantity
            
            # Remove from pending orders
            inventory.pending_orders = [
                order for order in inventory.pending_orders
                if order.get("order_id") != order_id
            ]
            
            await self.read_store.upsert_inventory(inventory)
            logger.info(f"Projected InventoryConfirmed: {product_id}, quantity: {quantity}")
            
        except Exception as e:
            logger.error(f"Error projecting InventoryConfirmed: {e}")
    
    async def handle_inventoryreleased(self, event: Dict[str, Any]):
        """Handle InventoryReleased event"""
        try:
            data = event.get("data", {})
            product_id = data.get("product_id")
            quantity = data.get("quantity", 0)
            order_id = data.get("order_id")
            
            # Get existing inventory
            inventory = await self.read_store.get_product_inventory(product_id)
            if not inventory:
                logger.warning(f"Inventory not found for InventoryReleased: {product_id}")
                return
            
            # Release reservation
            inventory.reserved_quantity -= quantity
            inventory.available_quantity = inventory.total_quantity - inventory.reserved_quantity
            
            # Remove from pending orders
            inventory.pending_orders = [
                order for order in inventory.pending_orders
                if order.get("order_id") != order_id
            ]
            
            await self.read_store.upsert_inventory(inventory)
            logger.info(f"Projected InventoryReleased: {product_id}, quantity: {quantity}")
            
        except Exception as e:
            logger.error(f"Error projecting InventoryReleased: {e}")
    
    async def handle_inventoryrestocked(self, event: Dict[str, Any]):
        """Handle InventoryRestocked event"""
        try:
            data = event.get("data", {})
            product_id = data.get("product_id")
            quantity = data.get("quantity", 0)
            
            # Get existing inventory
            inventory = await self.read_store.get_product_inventory(product_id)
            if not inventory:
                # Create new inventory record
                inventory = InventoryReadModel()
                inventory.product_id = product_id
                inventory.product_name = data.get("product_name", f"Product {product_id}")
                inventory.reorder_level = data.get("reorder_level", 10)
            
            # Update quantities
            inventory.total_quantity += quantity
            inventory.available_quantity = inventory.total_quantity - inventory.reserved_quantity
            inventory.last_restocked = datetime.fromisoformat(event.get("timestamp"))
            
            await self.read_store.upsert_inventory(inventory)
            logger.info(f"Projected InventoryRestocked: {product_id}, quantity: {quantity}")
            
        except Exception as e:
            logger.error(f"Error projecting InventoryRestocked: {e}")

class UserSummaryProjector(EventProjector):
    """Projector for user summary events"""
    
    async def handle_orderpaid(self, event: Dict[str, Any]):
        """Update user summary when order is paid"""
        try:
            data = event.get("data", {})
            user_id = data.get("user_id")
            amount = data.get("amount", 0.0)
            
            if not user_id:
                logger.warning("No user_id in OrderPaid event")
                return
            
            # Get existing summary
            summary = await self.read_store.get_user_summary(user_id)
            if not summary:
                summary = UserOrderSummaryReadModel()
                summary.user_id = user_id
                summary.user_email = data.get("user_email", "")
            
            # Update stats
            summary.total_orders += 1
            summary.total_spent += amount
            summary.avg_order_value = summary.total_spent / summary.total_orders
            summary.last_order_date = datetime.fromisoformat(event.get("timestamp"))
            
            # Update status counts
            if "COMPLETED" not in summary.order_statuses:
                summary.order_statuses["COMPLETED"] = 0
            summary.order_statuses["COMPLETED"] += 1
            
            await self.read_store.upsert_user_summary(summary)
            logger.info(f"Updated user summary for OrderPaid: {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating user summary for OrderPaid: {e}")

class CQRSProjectionService:
    """Service that coordinates all event projectors"""
    
    def __init__(self, read_store: CQRSReadStore):
        self.read_store = read_store
        self.projectors = [
            OrderProjector(read_store),
            InventoryProjector(read_store),
            UserSummaryProjector(read_store)
        ]
        self.subscriber = None
    
    async def start(self):
        """Start the projection service"""
        try:
            # Connect to read store
            await self.read_store.connect()
            
            # Setup event subscriber
            self.subscriber = EventSubscriber()
            
            # Subscribe to all events for projection
            await self.subscriber.subscribe_to_pattern(
                "*.#",  # All events from all services
                self._handle_event
            )
            
            logger.info("CQRS Projection Service started")
            
        except Exception as e:
            logger.error(f"Error starting CQRS Projection Service: {e}")
            raise
    
    async def stop(self):
        """Stop the projection service"""
        try:
            if self.subscriber:
                await self.subscriber.close()
            
            await self.read_store.disconnect()
            
            logger.info("CQRS Projection Service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping CQRS Projection Service: {e}")
    
    async def _handle_event(self, channel, method, properties, body):
        """Handle incoming events for projection"""
        try:
            import json
            event = json.loads(body)
            
            logger.debug(f"Projecting event: {event.get('event_type')}")
            
            # Project event with all projectors
            for projector in self.projectors:
                await projector.project_event(event)
            
            # Acknowledge the message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error handling event for projection: {e}")
            # Reject the message (will be requeued)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
