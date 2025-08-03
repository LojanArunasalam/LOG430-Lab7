# Event Store FastAPI Application with MongoDB

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import uvicorn
import logging
import sys
import os
from datetime import datetime
import threading
import time

# Add parent directory to path for imports
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.events.subscriber import EventSubscriber
from repository_mongo import EventStoreRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Event Store API", 
    description="MongoDB-based Event Store for Event Sourcing",
    version="1.0.0"
)

# Global repository instance
repository = EventStoreRepository()

# Event subscriber for capturing all events
event_subscriber = None
consumer_thread = None

@app.on_event("startup")
async def startup_event():
    """Initialize event subscriber on startup"""
    global event_subscriber, consumer_thread
    
    logger.info("Starting Event Store with MongoDB...")
    
    try:
        # Initialize event subscriber
        event_subscriber = EventSubscriber("event-store")
        
        # Subscribe to all events using wildcard pattern
        event_subscriber.subscribe_to_event(
            exchange="orders",
            routing_key="order.*",
            handler=handle_event
        )
        
        event_subscriber.subscribe_to_event(
            exchange="inventory",
            routing_key="inventory.*",
            handler=handle_event
        )
        
        event_subscriber.subscribe_to_event(
            exchange="payments",
            routing_key="payment.*",
            handler=handle_event
        )
        
        event_subscriber.subscribe_to_event(
            exchange="notifications",
            routing_key="notification.*",
            handler=handle_event
        )
        
        # Start consuming in background
        consumer_thread = event_subscriber.start_consuming_in_background()
        
        logger.info("Event Store started successfully with MongoDB backend")
        
    except Exception as e:
        logger.error(f"Error starting Event Store: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global event_subscriber
    
    if event_subscriber:
        event_subscriber.close()
    
    logger.info("Event Store shutdown complete")

def handle_event(event_data: Dict[str, Any]):
    """Handle incoming events and store them"""
    try:
        logger.info(f"Storing event: {event_data.get('event_type', 'unknown')}")
        
        # Store event in MongoDB
        success = repository.store_event(event_data)
        
        if success:
            logger.info(f"Event stored successfully: {event_data.get('event_id')}")
        else:
            logger.error(f"Failed to store event: {event_data.get('event_id')}")
            
    except Exception as e:
        logger.error(f"Error handling event: {e}")

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Event Store",
        "status": "running",
        "backend": "MongoDB",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    try:
        # Test MongoDB connection
        stats = repository.get_event_statistics()
        
        return {
            "status": "healthy",
            "backend": "MongoDB",
            "total_events": stats.get("total_events", 0),
            "subscriber_active": consumer_thread.is_alive() if consumer_thread else False,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/events")
async def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    aggregate_type: Optional[str] = Query(None, description="Filter by aggregate type"),
    aggregate_id: Optional[str] = Query(None, description="Filter by aggregate ID"),
    correlation_id: Optional[str] = Query(None, description="Filter by correlation ID"),
    limit: int = Query(100, description="Maximum number of events to return")
):
    """Get events with optional filtering"""
    try:
        if aggregate_type and aggregate_id:
            events = repository.get_events_by_aggregate(aggregate_type, aggregate_id)
        elif event_type:
            events = repository.get_events_by_type(event_type, limit)
        elif correlation_id:
            events = repository.get_events_by_correlation(correlation_id, limit)
        else:
            events = repository.get_all_events(limit)
        
        return {
            "events": events,
            "count": len(events),
            "filters": {
                "event_type": event_type,
                "aggregate_type": aggregate_type,
                "aggregate_id": aggregate_id,
                "correlation_id": correlation_id,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/replay")
async def replay_aggregate(
    aggregate_type: str = Query(..., description="Type of aggregate to replay"),
    aggregate_id: str = Query(..., description="ID of aggregate to replay")
):
    """Replay events for a specific aggregate"""
    try:
        result = repository.replay_aggregate_events(aggregate_type, aggregate_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/statistics")
async def get_statistics():
    """Get event store statistics"""
    try:
        stats = repository.get_event_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/demo/order-lifecycle")
async def demo_order_lifecycle():
    """Demo endpoint showing a complete order lifecycle through events"""
    try:
        # Find the most recent order correlation ID
        recent_orders = repository.get_events_by_type("OrderInitiated", limit=5)
        
        if not recent_orders:
            return {
                "message": "No orders found. Create an order first!",
                "suggestion": "POST to /ecommerce/checkout/initiate to create a test order"
            }
        
        # Get the correlation ID from the most recent order
        correlation_id = recent_orders[0].get('correlation_id')
        
        if not correlation_id:
            return {"error": "No correlation ID found in recent orders"}
        
        # Get all events for this correlation ID
        related_events = repository.get_events_by_correlation(correlation_id)
        
        # Organize events by timeline
        timeline = []
        for event in related_events:
            timeline.append({
                "timestamp": event.get('timestamp'),
                "event_type": event.get('event_type'),
                "service": event.get('metadata', {}).get('service', 'unknown'),
                "data": event.get('data', {})
            })
        
        return {
            "correlation_id": correlation_id,
            "total_events": len(timeline),
            "timeline": timeline,
            "description": "Complete order lifecycle showing event flow across microservices"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/snapshots")
async def create_snapshot(
    aggregate_type: str,
    aggregate_id: str
):
    """Create a snapshot for an aggregate"""
    try:
        # Get current state by replaying events
        replay_result = repository.replay_aggregate_events(aggregate_type, aggregate_id)
        
        if replay_result.get("current_state"):
            # Store snapshot
            success = repository.store_snapshot(
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                snapshot_data=replay_result["current_state"],
                version=replay_result["current_state"].get("version", 1)
            )
            
            if success:
                return {
                    "message": "Snapshot created successfully",
                    "aggregate_type": aggregate_type,
                    "aggregate_id": aggregate_id,
                    "version": replay_result["current_state"].get("version", 1)
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to create snapshot")
        else:
            raise HTTPException(status_code=404, detail="No events found for aggregate")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/snapshots/{aggregate_type}/{aggregate_id}")
async def get_snapshot(aggregate_type: str, aggregate_id: str):
    """Get snapshot for an aggregate"""
    try:
        snapshot = repository.get_snapshot(aggregate_type, aggregate_id)
        
        if snapshot:
            return snapshot
        else:
            raise HTTPException(status_code=404, detail="Snapshot not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
