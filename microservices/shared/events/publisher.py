# Event Publisher for RabbitMQ

import pika
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self, rabbitmq_url: str = "amqp://admin:admin@rabbitmq:5672/"):
        """Initialize RabbitMQ connection for publishing events"""
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            self.channel = self.connection.channel()
            
            # Declare exchanges for different domains
            self._declare_exchanges()
            logger.info("EventPublisher initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize EventPublisher: {e}")
            raise
    
    def _declare_exchanges(self):
        """Declare all required exchanges"""
        exchanges = [
            'ecommerce.orders',
            'ecommerce.inventory', 
            'ecommerce.payments',
            'ecommerce.shipping',
            'ecommerce.notifications',
            'ecommerce.analytics'
        ]
        
        for exchange in exchanges:
            self.channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
    
    def publish_event(self, 
                     event_type: str, 
                     aggregate_type: str, 
                     aggregate_id: str, 
                     data: Dict[str, Any],
                     correlation_id: Optional[str] = None,
                     service_name: str = "unknown") -> str:
        """
        Publish an event to RabbitMQ
        
        Args:
            event_type: Type of event (e.g., OrderCreated, StockReserved)
            aggregate_type: Domain object type (e.g., Order, Inventory, Payment)
            aggregate_id: Unique identifier for the aggregate
            data: Event payload data
            correlation_id: Optional correlation ID for tracking
            service_name: Name of the publishing service
            
        Returns:
            event_id: Unique identifier for the published event
        """
        
        event_id = str(uuid.uuid4())
        
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id,
            "version": 1,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data,
            "metadata": {
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "service": service_name,
                "published_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        try:
            # Determine exchange and routing key
            exchange = f"ecommerce.{aggregate_type.lower()}"
            routing_key = f"{aggregate_type.lower()}.{event_type.lower()}"
            
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(event),
                properties=pika.BasicProperties(
                    content_type='application/json',
                    message_id=event_id,
                    correlation_id=event["metadata"]["correlation_id"],
                    delivery_mode=2  # Make message persistent
                )
            )
            
            logger.info(f"Published event: {event_type} for {aggregate_type} {aggregate_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            raise
    
    def close(self):
        """Close the connection"""
        if hasattr(self, 'connection') and not self.connection.is_closed:
            self.connection.close()
            logger.info("EventPublisher connection closed")
