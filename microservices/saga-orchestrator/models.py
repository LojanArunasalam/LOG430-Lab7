from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from enum import Enum

Base = declarative_base()

class OrderState(Enum):
    CREATED = "created"
    STOCK_VERIFIED = "stock_verified"
    STOCK_RESERVED = "stock_reserved"
    PAYMENT_PROCESSED = "payment_processed"
    ORDER_CONFIRMED = "order_confirmed"
    COMPENSATION_STARTED = "compensation_started"
    CANCELLED = "cancelled"

class SagaStatus(Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

class SagaInstance(Base):
    __tablename__ = "saga_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, nullable=False)
    customer_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    store_id = Column(Integer, nullable=False)
    cart_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(DECIMAL(10, 2))
    current_state = Column(String(50), default=OrderState.CREATED.value)
    saga_status = Column(String(50), default=SagaStatus.STARTED.value)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    error_message = Column(Text)
    compensation_actions = Column(Text)
    checkout_id = Column(Integer)

class SagaStep(Base):
    __tablename__ = "saga_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    saga_id = Column(Integer, ForeignKey("saga_instances.id"), nullable=False)
    step_name = Column(String(100), nullable=False)
    step_status = Column(String(50), nullable=False)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    error_message = Column(Text)
    request_data = Column(Text)
    response_data = Column(Text)

