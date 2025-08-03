# Notification Service - Event-Driven Email/SMS Notifications

from fastapi import FastAPI, HTTPException
import sys
import threading
import time
import logging
from typing import Dict, Any
from datetime import datetime

# Add shared directory to path
sys.path.append('/app/../shared')
from events import (
    EventPublisher, 
    EventSubscriber,
    NotificationEvents, 
    AggregateTypes,
    Exchanges,
    RoutingKeys
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service")

# Event infrastructure
event_publisher = None
event_subscriber = None

def get_event_publisher():
    """Get or create event publisher instance"""
    global event_publisher
    if event_publisher is None:
        try:
            event_publisher = EventPublisher()
            logger.info("Notification event publisher initialized")
        except Exception as e:
            logger.error(f"Failed to initialize event publisher: {e}")
            event_publisher = None
    return event_publisher

# Business Logic
def send_email_notification(recipient: str, subject: str, content: str) -> Dict[str, Any]:
    """
    Simulate sending email notification
    
    Returns:
        Dict with notification result information
    """
    logger.info(f"Sending email to {recipient}: {subject}")
    
    # Simulate email sending delay
    time.sleep(1)
    
    # In real implementation, you'd use SendGrid, AWS SES, etc.
    message_id = f"msg_{int(time.time())}_{hash(recipient) % 10000}"
    
    return {
        "success": True,
        "message_id": message_id,
        "recipient": recipient,
        "subject": subject,
        "sent_at": datetime.utcnow().isoformat(),
        "delivery_status": "sent"
    }

def send_sms_notification(phone: str, message: str) -> Dict[str, Any]:
    """
    Simulate sending SMS notification
    
    Returns:
        Dict with SMS result information
    """
    logger.info(f"Sending SMS to {phone}: {message[:50]}...")
    
    # Simulate SMS sending delay
    time.sleep(0.5)
    
    message_id = f"sms_{int(time.time())}_{hash(phone) % 10000}"
    
    return {
        "success": True,
        "message_id": message_id,
        "recipient": phone,
        "sent_at": datetime.utcnow().isoformat(),
        "delivery_status": "sent"
    }

# Event Handlers
def handle_order_created(event_data: dict):
    """Handle OrderCreated event - send order confirmation"""
    try:
        order_data = event_data["data"]
        order_id = order_data["order_id"]
        customer_id = order_data["customer_id"]
        total_amount = order_data.get("total_amount", 0)
        correlation_id = event_data["metadata"]["correlation_id"]
        
        logger.info(f"Sending order confirmation for order {order_id}")
        
        # Simulate getting customer email (in real scenario, call users service)
        customer_email = f"customer{customer_id}@example.com"
        
        # Send order confirmation email
        email_result = send_email_notification(
            recipient=customer_email,
            subject=f"Order Confirmation - Order #{order_id}",
            content=f"Your order #{order_id} for ${total_amount} has been confirmed and is being processed."
        )
        
        publisher = get_event_publisher()
        if publisher:
            # Publish OrderConfirmationSent event
            publisher.publish_event(
                event_type=NotificationEvents.ORDER_CONFIRMATION_SENT,
                aggregate_type=AggregateTypes.NOTIFICATION,
                aggregate_id=email_result["message_id"],
                data={
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "notification_type": "email",
                    "recipient": customer_email,
                    "message_id": email_result["message_id"],
                    "sent_at": email_result["sent_at"],
                    "subject": f"Order Confirmation - Order #{order_id}"
                },
                correlation_id=correlation_id,
                service_name="notification"
            )
        
        logger.info(f"Order confirmation sent for order {order_id}")
        
    except Exception as e:
        logger.error(f"Error handling OrderCreated event: {e}")

def handle_payment_processed(event_data: dict):
    """Handle PaymentProcessed event - send payment confirmation"""
    try:
        payment_data = event_data["data"]
        order_id = payment_data["order_id"]
        payment_id = payment_data["payment_id"]
        amount = payment_data["amount"]
        correlation_id = event_data["metadata"]["correlation_id"]
        
        logger.info(f"Sending payment confirmation for order {order_id}")
        
        # Simulate getting customer contact info
        customer_email = f"customer@example.com"  # In real scenario, get from users service
        
        # Send payment confirmation
        email_result = send_email_notification(
            recipient=customer_email,
            subject=f"Payment Processed - Order #{order_id}",
            content=f"Payment of ${amount} for order #{order_id} has been processed successfully. Payment ID: {payment_id}"
        )
        
        publisher = get_event_publisher()
        if publisher:
            # Publish notification sent event
            publisher.publish_event(
                event_type=NotificationEvents.ORDER_CONFIRMATION_SENT,
                aggregate_type=AggregateTypes.NOTIFICATION,
                aggregate_id=email_result["message_id"],
                data={
                    "order_id": order_id,
                    "payment_id": payment_id,
                    "notification_type": "email",
                    "recipient": customer_email,
                    "message_id": email_result["message_id"],
                    "sent_at": email_result["sent_at"],
                    "subject": f"Payment Processed - Order #{order_id}"
                },
                correlation_id=correlation_id,
                service_name="notification"
            )
        
        logger.info(f"Payment confirmation sent for order {order_id}")
        
    except Exception as e:
        logger.error(f"Error handling PaymentProcessed event: {e}")

def handle_payment_failed(event_data: dict):
    """Handle PaymentFailed event - send payment failure notification"""
    try:
        payment_data = event_data["data"]
        order_id = payment_data["order_id"]
        failure_reason = payment_data.get("failure_reason", "unknown")
        correlation_id = event_data["metadata"]["correlation_id"]
        
        logger.info(f"Sending payment failure notification for order {order_id}")
        
        # Simulate getting customer contact info
        customer_email = f"customer@example.com"
        
        # Send payment failure notification
        email_result = send_email_notification(
            recipient=customer_email,
            subject=f"Payment Failed - Order #{order_id}",
            content=f"Payment for order #{order_id} failed. Reason: {failure_reason}. Please try again or contact support."
        )
        
        logger.info(f"Payment failure notification sent for order {order_id}")
        
    except Exception as e:
        logger.error(f"Error handling PaymentFailed event: {e}")

def handle_order_events(event_data: dict):
    """Generic handler for all order events"""
    try:
        event_type = event_data.get('event_type', '')
        
        if event_type == 'OrderCreated':
            handle_order_created(event_data)
        else:
            logger.info(f"Received order event: {event_type} - not handled")
            
    except Exception as e:
        logger.error(f"Error handling order event: {e}")

def handle_payment_events(event_data: dict):
    """Generic handler for all payment events"""
    try:
        event_type = event_data.get('event_type', '')
        
        if event_type == 'PaymentProcessed':
            handle_payment_processed(event_data)
        elif event_type == 'PaymentFailed':
            handle_payment_failed(event_data)
        else:
            logger.info(f"Received payment event: {event_type} - not handled")
            
    except Exception as e:
        logger.error(f"Error handling payment event: {e}")

def start_event_consumer():
    """Start the event consumer in a background thread"""
    global event_subscriber
    
    def consumer_loop():
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                event_subscriber = EventSubscriber("notification_service")
                
                # Subscribe to various events
                # Publisher logic: exchange = f"ecommerce.{aggregate_type.lower()}" 
                # Publisher logic: routing_key = f"{aggregate_type.lower()}.{event_type.lower()}"
                
                event_subscriber.subscribe_to_event(
                    exchange="orders",  # This will match the exchanges declared by the publisher
                    routing_key="order.*",  # Use wildcard to catch all order events
                    handler=handle_order_events
                )
                
                event_subscriber.subscribe_to_event(
                    exchange="payments",  # This will match the exchanges declared by the publisher
                    routing_key="payment.*",  # Use wildcard to catch all payment events
                    handler=handle_payment_events
                )
                
                logger.info("Notification event consumer subscribed to events")
                event_subscriber.start_consuming()
                break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Notification event consumer failed (attempt {retry_count}): {e}")
                if retry_count < max_retries:
                    time.sleep(5)  # Wait before retry
                else:
                    logger.error("Max retries reached. Notification event consumer will not start.")
    
    consumer_thread = threading.Thread(target=consumer_loop)
    consumer_thread.daemon = True
    consumer_thread.start()
    logger.info("Notification event consumer thread started")

# API Endpoints
@app.get("/")
def read_root():
    return {
        "message": "Notification Service is running",
        "service": "notification",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "notification",
        "timestamp": time.time()
    }

@app.post("/api/v1/notifications/email")
def send_manual_email(recipient: str, subject: str, content: str):
    """Manual email sending endpoint for testing"""
    try:
        result = send_email_notification(recipient, subject, content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

@app.post("/api/v1/notifications/sms")
def send_manual_sms(phone: str, message: str):
    """Manual SMS sending endpoint for testing"""
    try:
        result = send_sms_notification(phone, message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS sending failed: {str(e)}")

# Initialize event consumer on startup
@app.on_event("startup")
async def startup_event():
    """Initialize event consumer when the app starts"""
    logger.info("Notification service starting up...")
    start_event_consumer()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up event connections on shutdown"""
    global event_publisher, event_subscriber
    
    logger.info("Notification service shutting down...")
    
    if event_subscriber:
        event_subscriber.close()
    
    if event_publisher:
        event_publisher.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
