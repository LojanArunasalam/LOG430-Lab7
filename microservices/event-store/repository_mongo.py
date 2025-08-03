# Event Store Repository for MongoDB

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
from models import event_store

logger = logging.getLogger(__name__)

class EventStoreRepository:
    """Repository for managing events in MongoDB Event Store"""
    
    def __init__(self):
        self.event_store = event_store
    
    def store_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Store an event in the Event Store
        
        Args:
            event_data: Event data dictionary containing event information
            
        Returns:
            bool: True if event was stored successfully
        """
        try:
            # Ensure required fields
            if 'event_id' not in event_data:
                event_data['event_id'] = str(uuid.uuid4())
            
            if 'timestamp' not in event_data:
                event_data['timestamp'] = datetime.utcnow()
            
            # Store in MongoDB
            return self.event_store.store_event(event_data)
            
        except Exception as e:
            logger.error(f"Error storing event: {e}")
            return False
    
    def get_all_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all events with optional limit"""
        return self.event_store.get_events(limit=limit)
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events filtered by type"""
        return self.event_store.get_events(event_type=event_type, limit=limit)
    
    def get_events_by_aggregate(self, aggregate_type: str, aggregate_id: str) -> List[Dict[str, Any]]:
        """Get all events for a specific aggregate"""
        return self.event_store.get_aggregate_events(aggregate_type, aggregate_id)
    
    def get_events_by_correlation(self, correlation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events by correlation ID"""
        return self.event_store.get_events(correlation_id=correlation_id, limit=limit)
    
    def replay_aggregate_events(self, aggregate_type: str, aggregate_id: str) -> Dict[str, Any]:
        """
        Replay events for an aggregate to reconstruct its state
        
        Args:
            aggregate_type: Type of the aggregate (e.g., 'Order', 'User')
            aggregate_id: Unique identifier of the aggregate
            
        Returns:
            Dict containing the replayed state and event history
        """
        try:
            # Get all events for this aggregate
            events = self.get_events_by_aggregate(aggregate_type, aggregate_id)
            
            if not events:
                return {
                    "aggregate_type": aggregate_type,
                    "aggregate_id": aggregate_id,
                    "current_state": None,
                    "event_count": 0,
                    "events": []
                }
            
            # Build current state by applying events in order
            current_state = self._apply_events_to_build_state(events, aggregate_type)
            
            # Format response
            return {
                "aggregate_type": aggregate_type,
                "aggregate_id": aggregate_id,
                "current_state": current_state,
                "event_count": len(events),
                "events": events
            }
            
        except Exception as e:
            logger.error(f"Error replaying aggregate events: {e}")
            return {
                "aggregate_type": aggregate_type,
                "aggregate_id": aggregate_id,
                "error": str(e),
                "current_state": None,
                "event_count": 0,
                "events": []
            }
    
    def _apply_events_to_build_state(self, events: List[Dict[str, Any]], aggregate_type: str) -> Dict[str, Any]:
        """
        Apply events in sequence to build the current aggregate state
        This is a simple implementation - in a real system you'd have 
        specific aggregate classes with apply methods
        """
        state = {
            "aggregate_type": aggregate_type,
            "version": 0,
            "created_at": None,
            "last_updated": None,
            "status": "unknown"
        }
        
        for event in events:
            event_type = event.get('event_type', '')
            event_data = event.get('data', {})
            
            # Update version
            state["version"] = event.get('version', state["version"] + 1)
            state["last_updated"] = event.get('timestamp')
            
            if state["created_at"] is None:
                state["created_at"] = event.get('timestamp')
            
            # Apply event-specific logic
            if aggregate_type == "Order":
                state = self._apply_order_event(state, event_type, event_data)
            elif aggregate_type == "User":
                state = self._apply_user_event(state, event_type, event_data)
            elif aggregate_type == "Product":
                state = self._apply_product_event(state, event_type, event_data)
            # Add more aggregate types as needed
            
        return state
    
    def _apply_order_event(self, state: Dict[str, Any], event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply order-specific events to build order state"""
        
        if event_type == "OrderInitiated":
            state.update({
                "user_id": event_data.get("user_id"),
                "status": "initiated",
                "items": event_data.get("items", []),
                "total_amount": event_data.get("total_amount", 0)
            })
        
        elif event_type == "OrderCreated":
            state.update({
                "status": "created",
                "order_details": event_data
            })
        
        elif event_type == "StockReserved":
            state.update({
                "status": "stock_reserved",
                "reserved_items": event_data.get("reserved_items", [])
            })
        
        elif event_type == "PaymentProcessed":
            state.update({
                "status": "payment_processed",
                "payment_id": event_data.get("payment_id"),
                "payment_status": event_data.get("status")
            })
        
        elif event_type == "OrderCompleted":
            state.update({
                "status": "completed"
            })
        
        elif event_type == "OrderCancelled":
            state.update({
                "status": "cancelled",
                "cancellation_reason": event_data.get("reason")
            })
        
        return state
    
    def _apply_user_event(self, state: Dict[str, Any], event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user-specific events"""
        if event_type == "UserCreated":
            state.update({
                "email": event_data.get("email"),
                "name": event_data.get("name"),
                "status": "active"
            })
        
        elif event_type == "UserUpdated":
            state.update(event_data)
        
        return state
    
    def _apply_product_event(self, state: Dict[str, Any], event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply product-specific events"""
        if event_type == "ProductCreated":
            state.update({
                "name": event_data.get("name"),
                "price": event_data.get("price"),
                "stock": event_data.get("stock"),
                "status": "available"
            })
        
        elif event_type == "StockUpdated":
            state.update({
                "stock": event_data.get("new_stock")
            })
        
        return state
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about events in the store"""
        return self.event_store.get_event_statistics()
    
    def store_snapshot(self, aggregate_type: str, aggregate_id: str, snapshot_data: Dict[str, Any], version: int) -> bool:
        """Store an aggregate snapshot for performance optimization"""
        return self.event_store.store_snapshot(aggregate_type, aggregate_id, snapshot_data, version)
    
    def get_snapshot(self, aggregate_type: str, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest snapshot for an aggregate"""
        return self.event_store.get_snapshot(aggregate_type, aggregate_id)
