# Event Store Repository

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_
from models import StoredEvent, EventSnapshot
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class EventStoreRepository:
    """Repository for managing event storage and retrieval"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def store_event(self, event_data: Dict[str, Any]) -> StoredEvent:
        """
        Store an event in the event store
        
        Args:
            event_data: Event dictionary with all event information
            
        Returns:
            StoredEvent: The stored event record
        """
        try:
            # Parse timestamp
            occurred_at = datetime.fromisoformat(
                event_data.get("timestamp", datetime.utcnow().isoformat()).replace("Z", "")
            )
            
            stored_event = StoredEvent(
                event_id=event_data["event_id"],
                event_type=event_data["event_type"],
                aggregate_type=event_data["aggregate_type"],
                aggregate_id=event_data["aggregate_id"],
                aggregate_version=event_data.get("version", 1),
                event_data=event_data["data"],
                metadata=event_data.get("metadata", {}),
                occurred_at=occurred_at,
                service_name=event_data.get("metadata", {}).get("service")
            )
            
            self.session.add(stored_event)
            self.session.commit()
            
            logger.info(f"Stored event {event_data['event_type']} for {event_data['aggregate_type']} {event_data['aggregate_id']}")
            return stored_event
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to store event: {e}")
            raise
    
    def get_events_by_aggregate(self, aggregate_type: str, aggregate_id: str, 
                               from_version: int = 0) -> List[StoredEvent]:
        """
        Get all events for a specific aggregate
        
        Args:
            aggregate_type: Type of aggregate (e.g., 'orders', 'inventory')
            aggregate_id: Unique identifier of the aggregate
            from_version: Start from this version (for incremental replay)
            
        Returns:
            List of stored events ordered by version
        """
        try:
            events = self.session.query(StoredEvent).filter(
                and_(
                    StoredEvent.aggregate_type == aggregate_type,
                    StoredEvent.aggregate_id == aggregate_id,
                    StoredEvent.aggregate_version >= from_version
                )
            ).order_by(asc(StoredEvent.aggregate_version)).all()
            
            logger.info(f"Retrieved {len(events)} events for {aggregate_type} {aggregate_id}")
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")
            raise
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[StoredEvent]:
        """
        Get events by type (useful for debugging/monitoring)
        
        Args:
            event_type: Type of event to retrieve
            limit: Maximum number of events to return
            
        Returns:
            List of stored events of the specified type
        """
        try:
            events = self.session.query(StoredEvent).filter(
                StoredEvent.event_type == event_type
            ).order_by(desc(StoredEvent.occurred_at)).limit(limit).all()
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve events by type: {e}")
            raise
    
    def get_all_events(self, limit: int = 1000, offset: int = 0) -> List[StoredEvent]:
        """
        Get all events (for global replay or analysis)
        
        Args:
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of all stored events ordered by occurrence time
        """
        try:
            events = self.session.query(StoredEvent).order_by(
                asc(StoredEvent.occurred_at)
            ).offset(offset).limit(limit).all()
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve all events: {e}")
            raise
    
    def get_events_by_correlation(self, correlation_id: str) -> List[StoredEvent]:
        """
        Get all events with the same correlation ID (trace a complete workflow)
        
        Args:
            correlation_id: Correlation ID to search for
            
        Returns:
            List of correlated events ordered by time
        """
        try:
            events = self.session.query(StoredEvent).filter(
                StoredEvent.metadata['correlation_id'].astext == correlation_id
            ).order_by(asc(StoredEvent.occurred_at)).all()
            
            logger.info(f"Retrieved {len(events)} events for correlation {correlation_id}")
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve events by correlation: {e}")
            raise
    
    def replay_events_for_aggregate(self, aggregate_type: str, aggregate_id: str) -> Dict[str, Any]:
        """
        Replay all events for an aggregate to reconstruct its current state
        
        Args:
            aggregate_type: Type of aggregate
            aggregate_id: Unique identifier of the aggregate
            
        Returns:
            Dictionary representing the current state of the aggregate
        """
        events = self.get_events_by_aggregate(aggregate_type, aggregate_id)
        
        # Initialize state based on aggregate type
        if aggregate_type == "orders":
            state = self._replay_order_events(events)
        elif aggregate_type == "inventory":
            state = self._replay_inventory_events(events)
        elif aggregate_type == "payments":
            state = self._replay_payment_events(events)
        else:
            # Generic replay
            state = self._replay_generic_events(events)
        
        state["_event_count"] = len(events)
        state["_last_updated"] = events[-1].occurred_at.isoformat() if events else None
        
        return state
    
    def _replay_order_events(self, events: List[StoredEvent]) -> Dict[str, Any]:
        """Replay order-specific events to reconstruct order state"""
        state = {
            "order_id": None,
            "customer_id": None,
            "status": "UNKNOWN",
            "total_amount": 0.0,
            "items": [],
            "payment_id": None,
            "created_at": None,
            "events_applied": []
        }
        
        for event in events:
            data = event.event_data
            
            if event.event_type == "OrderInitiated":
                state.update({
                    "order_id": data.get("order_id"),
                    "customer_id": data.get("customer_id"),
                    "status": "INITIATED",
                    "total_amount": data.get("total_amount", 0),
                    "items": data.get("items", []),
                    "created_at": event.occurred_at.isoformat()
                })
            
            elif event.event_type == "OrderCreated":
                state["status"] = "CREATED"
            
            elif event.event_type == "PaymentProcessed":
                state.update({
                    "status": "PAYMENT_PROCESSED",
                    "payment_id": data.get("payment_id")
                })
            
            elif event.event_type == "OrderConfirmed":
                state["status"] = "CONFIRMED"
            
            elif event.event_type == "OrderCancelled":
                state.update({
                    "status": "CANCELLED",
                    "cancellation_reason": data.get("cancellation_reason")
                })
            
            state["events_applied"].append({
                "event_type": event.event_type,
                "occurred_at": event.occurred_at.isoformat()
            })
        
        return state
    
    def _replay_inventory_events(self, events: List[StoredEvent]) -> Dict[str, Any]:
        """Replay inventory-specific events to reconstruct stock state"""
        state = {
            "store_id": None,
            "products": {},
            "reservations": {},
            "events_applied": []
        }
        
        for event in events:
            data = event.event_data
            
            if event.event_type == "StockReserved":
                reservation_id = data.get("reservation_id")
                state["reservations"][reservation_id] = {
                    "order_id": data.get("order_id"),
                    "items": data.get("items", []),
                    "reserved_at": event.occurred_at.isoformat()
                }
            
            elif event.event_type == "StockReleased":
                reservation_id = data.get("reservation_id")
                if reservation_id in state["reservations"]:
                    del state["reservations"][reservation_id]
            
            state["events_applied"].append({
                "event_type": event.event_type,
                "occurred_at": event.occurred_at.isoformat()
            })
        
        return state
    
    def _replay_payment_events(self, events: List[StoredEvent]) -> Dict[str, Any]:
        """Replay payment-specific events to reconstruct payment state"""
        state = {
            "order_id": None,
            "payment_id": None,
            "status": "UNKNOWN",
            "amount": 0.0,
            "currency": "CAD",
            "events_applied": []
        }
        
        for event in events:
            data = event.event_data
            
            if event.event_type == "PaymentProcessed":
                state.update({
                    "order_id": data.get("order_id"),
                    "payment_id": data.get("payment_id"),
                    "status": "PROCESSED",
                    "amount": data.get("amount", 0),
                    "currency": data.get("currency", "CAD")
                })
            
            elif event.event_type == "PaymentFailed":
                state.update({
                    "status": "FAILED",
                    "failure_reason": data.get("failure_reason")
                })
            
            elif event.event_type == "PaymentRefunded":
                state["status"] = "REFUNDED"
            
            state["events_applied"].append({
                "event_type": event.event_type,
                "occurred_at": event.occurred_at.isoformat()
            })
        
        return state
    
    def _replay_generic_events(self, events: List[StoredEvent]) -> Dict[str, Any]:
        """Generic event replay for unknown aggregate types"""
        state = {
            "aggregate_id": events[0].aggregate_id if events else None,
            "aggregate_type": events[0].aggregate_type if events else None,
            "events_applied": []
        }
        
        for event in events:
            state["events_applied"].append({
                "event_type": event.event_type,
                "data": event.event_data,
                "occurred_at": event.occurred_at.isoformat()
            })
        
        return state
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored events"""
        try:
            total_events = self.session.query(StoredEvent).count()
            
            # Count by event type
            event_type_counts = {}
            results = self.session.query(
                StoredEvent.event_type, 
                self.session.query(StoredEvent).filter(
                    StoredEvent.event_type == StoredEvent.event_type
                ).count()
            ).distinct().all()
            
            # Count by aggregate type
            aggregate_type_counts = {}
            agg_results = self.session.query(
                StoredEvent.aggregate_type
            ).distinct().all()
            
            for agg_type in agg_results:
                count = self.session.query(StoredEvent).filter(
                    StoredEvent.aggregate_type == agg_type[0]
                ).count()
                aggregate_type_counts[agg_type[0]] = count
            
            return {
                "total_events": total_events,
                "aggregate_types": aggregate_type_counts,
                "unique_event_types": len(set(r[0] for r in results))
            }
            
        except Exception as e:
            logger.error(f"Failed to get event statistics: {e}")
            return {"error": str(e)}
