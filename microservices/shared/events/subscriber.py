# Event Subscriber for RabbitMQ

import pika
import json
import threading
from typing import Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EventSubscriber:
    def __init__(self, service_name: str, rabbitmq_url: str = "amqp://admin:admin@rabbitmq:5672/"):
        """Initialize RabbitMQ connection for subscribing to events"""
        self.service_name = service_name
        self.rabbitmq_url = rabbitmq_url
        self.handlers: Dict[str, Callable] = {}
        self.connection = None
        self.channel = None
        
    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            self.channel = self.connection.channel()
            logger.info(f"EventSubscriber for {self.service_name} connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def subscribe_to_event(self, exchange: str, routing_key: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to a specific event type
        
        Args:
            exchange: RabbitMQ exchange name
            routing_key: Routing key pattern to match
            handler: Function to handle the event data
        """
        
        if not self.connection:
            self._connect()
        
        # Declare exchange to ensure it exists (idempotent operation)
        self.channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
        
        # Create a unique queue for this service and event type
        queue_name = f"{self.service_name}_{routing_key.replace('.', '_')}"
        
        # Declare queue with durability
        self.channel.queue_declare(queue=queue_name, durable=True)
        
        # Bind queue to exchange with routing key
        self.channel.queue_bind(
            exchange=exchange,
            queue=queue_name,
            routing_key=routing_key
        )
        
        # Store handler for this routing key
        self.handlers[routing_key] = handler
        
        def wrapper(ch, method, properties, body):
            """Wrapper function to handle message processing"""
            try:
                event_data = json.loads(body)
                event_type = event_data.get('event_type', 'unknown')
                
                logger.info(f"Received event: {event_type} on {routing_key}")
                
                # Call the business logic handler
                handler(event_data)
                
                # Acknowledge the message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Successfully processed event: {event_type}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in event message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                # Requeue the message for retry
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # Set up consumer
        self.channel.basic_qos(prefetch_count=1)  # Process one message at a time
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapper
        )
        
        logger.info(f"Subscribed to {routing_key} on exchange {exchange}")
    
    def start_consuming(self):
        """Start listening for events (blocking call)"""
        if not self.connection:
            self._connect()
            
        logger.info(f"Starting event consumer for {self.service_name}...")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping event consumer...")
            self.channel.stop_consuming()
            self.connection.close()
    
    def start_consuming_in_background(self):
        """Start consuming events in a background thread"""
        consumer_thread = threading.Thread(target=self.start_consuming)
        consumer_thread.daemon = True
        consumer_thread.start()
        logger.info(f"Event consumer for {self.service_name} started in background")
        return consumer_thread
    
    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.channel.stop_consuming()
            self.connection.close()
            logger.info(f"EventSubscriber for {self.service_name} connection closed")
