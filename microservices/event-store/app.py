# Event Store Service

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Any, Optional
import sys
import threading
import time
import logging
import os
from contextlib import asynccontextmanager

# Add shared directory to path
sys.path.append('/app/../shared')
from events import EventSubscriber

from models import Base, StoredEvent
from repository import EventStoreRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL_EVENT_STORE", "postgresql://admin:admin@db_event_store:5432/postgres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Event subscriber for capturing all events
event_subscriber = None

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown"""
    # Startup
    logger.info("Creating Event Store database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Starting event capture...")
    start_event_capture()
    yield
    # Shutdown
    global event_subscriber
    if event_subscriber:
        event_subscriber.close()

app = FastAPI(
    title="Event Store Service",
    description="Persistent storage and replay of domain events",
    version="1.0.0",
    lifespan=lifespan
)

# Event capture handlers
def handle_all_events(event_data: dict):
    """Capture and store all events that flow through the system"""
    try:
        db = SessionLocal()
        repo = EventStoreRepository(db)
        
        # Store the event
        stored_event = repo.store_event(event_data)
        
        logger.info(f"Captured and stored event: {event_data['event_type']} for {event_data['aggregate_type']} {event_data['aggregate_id']}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Failed to capture event: {e}")

def start_event_capture():
    """Start capturing all events from RabbitMQ"""
    global event_subscriber
    
    def capture_loop():
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                event_subscriber = EventSubscriber("event_store")
                
                # Subscribe to ALL events using wildcard routing
                exchanges = [
                    "ecommerce.orders",
                    "ecommerce.inventory", 
                    "ecommerce.payments",
                    "ecommerce.shipping",
                    "ecommerce.notifications"
                ]
                
                for exchange in exchanges:
                    # Use wildcard to capture all events in each exchange
                    event_subscriber.subscribe_to_event(
                        exchange=exchange,
                        routing_key="#",  # Wildcard - capture everything
                        handler=handle_all_events
                    )
                
                logger.info("Event Store consumer subscribed to all events")
                event_subscriber.start_consuming()
                break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Event capture failed (attempt {retry_count}): {e}")
                if retry_count < max_retries:
                    time.sleep(5)
                else:
                    logger.error("Max retries reached. Event capture will not start.")
    
    capture_thread = threading.Thread(target=capture_loop)
    capture_thread.daemon = True
    capture_thread.start()
    logger.info("Event capture thread started")

# API Endpoints

@app.get("/")
def read_root():
    return {
        "message": "Event Store Service is running",
        "service": "event-store",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "event-store",
        "timestamp": time.time()
    }

@app.get("/api/v1/events")
def get_all_events(
    limit: int = Query(100, description="Maximum number of events to return"),
    offset: int = Query(0, description="Number of events to skip"),
    db: Session = Depends(get_db)
):
    """Get all stored events with pagination"""
    try:
        repo = EventStoreRepository(db)
        events = repo.get_all_events(limit=limit, offset=offset)
        
        return {
            "events": [event.to_dict() for event in events],
            "count": len(events),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")

@app.get("/api/v1/events/type/{event_type}")
def get_events_by_type(
    event_type: str,
    limit: int = Query(100, description="Maximum number of events to return"),
    db: Session = Depends(get_db)
):
    """Get events by specific type"""
    try:
        repo = EventStoreRepository(db)
        events = repo.get_events_by_type(event_type, limit=limit)
        
        return {
            "event_type": event_type,
            "events": [event.to_dict() for event in events],
            "count": len(events)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events by type: {str(e)}")

@app.get("/api/v1/events/aggregate/{aggregate_type}/{aggregate_id}")
def get_events_by_aggregate(
    aggregate_type: str,
    aggregate_id: str,
    from_version: int = Query(0, description="Start from this version"),
    db: Session = Depends(get_db)
):
    """Get all events for a specific aggregate"""
    try:
        repo = EventStoreRepository(db)
        events = repo.get_events_by_aggregate(aggregate_type, aggregate_id, from_version)
        
        return {
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id,
            "events": [event.to_dict() for event in events],
            "count": len(events),
            "from_version": from_version
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve aggregate events: {str(e)}")

@app.get("/api/v1/events/correlation/{correlation_id}")
def get_events_by_correlation(
    correlation_id: str,
    db: Session = Depends(get_db)
):
    """Get all events with the same correlation ID (trace a complete workflow)"""
    try:
        repo = EventStoreRepository(db)
        events = repo.get_events_by_correlation(correlation_id)
        
        return {
            "correlation_id": correlation_id,
            "events": [event.to_dict() for event in events],
            "count": len(events),
            "workflow_trace": [
                {
                    "step": i + 1,
                    "event_type": event.event_type,
                    "service": event.service_name,
                    "occurred_at": event.occurred_at.isoformat()
                }
                for i, event in enumerate(events)
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve correlated events: {str(e)}")

@app.get("/api/v1/replay/aggregate/{aggregate_type}/{aggregate_id}")
def replay_aggregate_events(
    aggregate_type: str,
    aggregate_id: str,
    db: Session = Depends(get_db)
):
    """Replay all events for an aggregate to reconstruct its current state"""
    try:
        repo = EventStoreRepository(db)
        current_state = repo.replay_events_for_aggregate(aggregate_type, aggregate_id)
        
        return {
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id,
            "current_state": current_state,
            "replayed_at": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to replay aggregate: {str(e)}")

@app.post("/api/v1/events/store")
def store_event_manually(event_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Manually store an event (for testing or external systems)"""
    try:
        repo = EventStoreRepository(db)
        stored_event = repo.store_event(event_data)
        
        return {
            "message": "Event stored successfully",
            "event_id": str(stored_event.event_id),
            "stored_at": stored_event.stored_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to store event: {str(e)}")

@app.get("/api/v1/statistics")
def get_event_statistics(db: Session = Depends(get_db)):
    """Get statistics about stored events"""
    try:
        repo = EventStoreRepository(db)
        stats = repo.get_event_statistics()
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/api/v1/replay/demo/order/{order_id}")
def demo_order_lifecycle(order_id: str, db: Session = Depends(get_db)):
    """Demo endpoint showing complete order lifecycle through events"""
    try:
        repo = EventStoreRepository(db)
        
        # Get all events for this order
        order_events = repo.get_events_by_aggregate("orders", order_id)
        
        if not order_events:
            raise HTTPException(status_code=404, detail=f"No events found for order {order_id}")
        
        # Replay to get current state
        current_state = repo.replay_events_for_aggregate("orders", order_id)
        
        # Get correlation ID from first event to trace complete workflow
        correlation_id = order_events[0].metadata.get("correlation_id") if order_events[0].metadata else None
        workflow_events = []
        
        if correlation_id:
            workflow_events = repo.get_events_by_correlation(correlation_id)
        
        return {
            "order_id": order_id,
            "current_state": current_state,
            "order_events": [event.to_dict() for event in order_events],
            "complete_workflow": [event.to_dict() for event in workflow_events],
            "lifecycle_summary": {
                "total_events": len(order_events),
                "status": current_state.get("status", "UNKNOWN"),
                "created_at": current_state.get("created_at"),
                "last_updated": current_state.get("_last_updated")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to demo order lifecycle: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
