# Payment Service - Event-Driven Payment Processing

from fastapi import FastAPI, HTTPException
import sys
import threading
import time
import uuid
import random
import logging
from typing import Dict, Any

# Add shared directory to path
sys.path.append('/app/../shared')
from events import (
    EventPublisher, 
    EventSubscriber,
    PaymentEvents, 
    AggregateTypes,
    Exchanges,
    RoutingKeys,
    create_payment_processed_data
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Payment Service")

# Event infrastructure
event_publisher = None
event_subscriber = None

def get_event_publisher():
    """Get or create event publisher instance"""
    global event_publisher
    if event_publisher is None:
        try:
            event_publisher = EventPublisher()
            logger.info("Payment event publisher initialized")
        except Exception as e:
            logger.error(f"Failed to initialize event publisher: {e}")
            event_publisher = None
    return event_publisher

# Business Logic
def process_payment(order_id: int, amount: float, payment_method: str = "credit_card") -> Dict[str, Any]:
    """
    Simulate payment processing
    
    Returns:
        Dict with payment result information
    """
    logger.info(f"Processing payment for order {order_id}, amount: ${amount}")
    
    # Simulate processing time
    time.sleep(2)
    
    # Simulate 85% success rate for realistic testing
    success = random.random() > 0.15
    
    payment_id = f"pay_{uuid.uuid4().hex[:8]}"
    
    if success:
        return {
            "success": True,
            "payment_id": payment_id,
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "amount": amount,
            "currency": "CAD",
            "payment_method": payment_method,
            "status": "PROCESSED"
        }
    else:
        return {
            "success": False,
            "payment_id": payment_id,
            "error_code": random.choice(["CARD_DECLINED", "INSUFFICIENT_FUNDS", "EXPIRED_CARD"]),
            "failure_reason": "payment_declined",
            "amount": amount,
            "status": "FAILED"
        }

# Event Handlers
def handle_stock_reserved(event_data: dict):
    """Handle StockReserved event - process payment"""
    try:
        stock_data = event_data["data"]
        order_id = stock_data["order_id"]
        correlation_id = event_data["metadata"]["correlation_id"]
        
        # For demo purposes, use a fixed amount or extract from order data
        amount = 99.99  # In real scenario, you'd get this from the order
        
        logger.info(f"Received StockReserved for order {order_id}, processing payment")
        
        publisher = get_event_publisher()
        if not publisher:
            logger.error("Event publisher not available")
            return
        
        # Process payment
        payment_result = process_payment(order_id, amount)
        
        if payment_result["success"]:
            # Publish PaymentProcessed event
            payment_data = create_payment_processed_data(
                order_id=order_id,
                payment_id=payment_result["payment_id"],
                amount=amount,
                currency="CAD"
            )
            
            publisher.publish_event(
                event_type=PaymentEvents.PAYMENT_PROCESSED,
                aggregate_type=AggregateTypes.PAYMENT,
                aggregate_id=payment_result["payment_id"],
                data=payment_data,
                correlation_id=correlation_id,
                service_name="payment"
            )
            
            logger.info(f"Payment processed successfully for order {order_id}")
            
        else:
            # Publish PaymentFailed event
            publisher.publish_event(
                event_type=PaymentEvents.PAYMENT_FAILED,
                aggregate_type=AggregateTypes.PAYMENT,
                aggregate_id=payment_result["payment_id"],
                data={
                    "order_id": order_id,
                    "payment_id": payment_result["payment_id"],
                    "amount": amount,
                    "failure_reason": payment_result["failure_reason"],
                    "error_code": payment_result["error_code"],
                    "failed_at": time.time()
                },
                correlation_id=correlation_id,
                service_name="payment"
            )
            
            logger.info(f"Payment failed for order {order_id}: {payment_result['failure_reason']}")
            
    except Exception as e:
        logger.error(f"Error handling StockReserved event: {e}")

def start_event_consumer():
    """Start the event consumer in a background thread"""
    global event_subscriber
    
    def consumer_loop():
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                event_subscriber = EventSubscriber("payment_service")
                
                # Subscribe to StockReserved events
                event_subscriber.subscribe_to_event(
                    exchange=Exchanges.INVENTORY,
                    routing_key=RoutingKeys.STOCK_RESERVED,
                    handler=handle_stock_reserved
                )
                
                logger.info("Payment event consumer subscribed to events")
                event_subscriber.start_consuming()
                break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Payment event consumer failed (attempt {retry_count}): {e}")
                if retry_count < max_retries:
                    time.sleep(5)  # Wait before retry
                else:
                    logger.error("Max retries reached. Payment event consumer will not start.")
    
    consumer_thread = threading.Thread(target=consumer_loop)
    consumer_thread.daemon = True
    consumer_thread.start()
    logger.info("Payment event consumer thread started")

# API Endpoints
@app.get("/")
def read_root():
    return {
        "message": "Payment Service is running",
        "service": "payment",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "payment",
        "timestamp": time.time()
    }

@app.post("/api/v1/payments/process")
def manual_payment_processing(order_id: int, amount: float):
    """Manual payment processing endpoint for testing"""
    try:
        result = process_payment(order_id, amount)
        return {
            "order_id": order_id,
            "payment_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")

# Initialize event consumer on startup
@app.on_event("startup")
async def startup_event():
    """Initialize event consumer when the app starts"""
    logger.info("Payment service starting up...")
    start_event_consumer()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up event connections on shutdown"""
    global event_publisher, event_subscriber
    
    logger.info("Payment service shutting down...")
    
    if event_subscriber:
        event_subscriber.close()
    
    if event_publisher:
        event_publisher.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
