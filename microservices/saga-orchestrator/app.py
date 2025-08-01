from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging
import os
from pydantic import BaseModel
from contextlib import asynccontextmanager

from models import Base
from saga_service import SagaService
from state_machine import OrderStateMachine
from typing import Optional
from datetime import datetime

class OrderCreateRequest(BaseModel):
    customer_id: int
    product_id: int
    store_id: int 
    quantity: int
    cart_id: int

class SagaResponse(BaseModel):
    saga_id: int
    order_id: int
    status: str
    current_state: str
    message: str
    created_at: datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
 
# Database setup
# DATABASE_URL_SAGA = os.getenv("DATABASE_URL_SAGA")
engine = create_engine("postgresql+psycopg2://admin:admin@db_saga:5432/postgres")
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Saga orchestrator started")
    yield
    # Shutdown
    logger.info("Saga orchestrator shutting down")

app = FastAPI(
    title="Saga Orchestrator Service",
    description="Orchestrates distributed transactions using the Saga pattern",
    version="1.0.0",
    lifespan=lifespan
)

# Dependency to get database session
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "service": "saga-orchestrator",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/start-saga", response_model=SagaResponse)
def start_saga(order_request: OrderCreateRequest, db: Session = Depends(get_db)):
    """
    Start a new order saga
    """
    try:
        logger.info(f"Starting saga for customer {order_request.customer_id}, product {order_request.product_id}")

        
        saga_service = SagaService(db)
        result = saga_service.start_order_saga(
            customer_id=order_request.customer_id,
            product_id=order_request.product_id,
            store_id=order_request.store_id,
            quantity=order_request.quantity,
            cart_id=order_request.cart_id
        )

        print(result)
        
        if result['status'] == "completed":
            return SagaResponse(
                saga_id=result['saga_id'],
                order_id=result['order_id'],
                status=result['status'],
                current_state=result['current_state'],
                message="Saga completed successfully",
                created_at=result.get('created_at')
            )
        else:
            print("Here 4")
            raise HTTPException(
                status_code=400,
                detail=f"Saga failed: {result.get('error_message', 'Unknown error')}"
            )
    except Exception as e:
        logger.error(f"Error starting saga: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/saga/{saga_id}")
def get_saga(saga_id: int, db: Session = Depends(get_db)):
    """
    Get saga status and history
    """
    try:
        saga_service = SagaService(db)
        result = saga_service.get_saga_status(saga_id)
        
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Saga not found")
            
    except Exception as e:
        logger.error(f"Error retrieving saga {saga_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/saga/order/{order_id}")
def get_saga_by_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get saga by order ID
    """
    try:
        state_machine = OrderStateMachine(db)
        saga = state_machine.get_saga_by_order(order_id)
        
        if saga:
            saga_service = SagaService(db)
            result = saga_service.get_saga_status(saga.id)
            return result
        else:
            raise HTTPException(status_code=404, detail="Saga not found for order")
            
    except Exception as e:
        logger.error(f"Error retrieving saga for order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def get_metrics():
    """
    Prometheus metrics endpoint
    """
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/sagas")
def list_sagas(db: Session = Depends(get_db)):
    """
    List all sagas (for monitoring/debugging)
    """
    try:
        from models import SagaInstance
        sagas = db.query(SagaInstance).order_by(SagaInstance.created_at.desc()).limit(50).all()
        
        return [
            {
                'saga_id': saga.id,
                'order_id': saga.order_id,
                'current_state': saga.current_state,
                'saga_status': saga.saga_status,
                'created_at': saga.created_at,
                'updated_at': saga.updated_at,
                'error_message': saga.error_message
            } for saga in sagas
        ]
        
    except Exception as e:
        logger.error(f"Error listing sagas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/saga/events")
def handle_microservice_event(event: dict):
    """Handle events from microservices"""
    try:
        saga_id = event.get("saga_id")
        event_type = event.get("event_type")
        success = event.get("success", True)
        data = event.get("data", {})
        service = event.get("service")
        
        session = Session()
        state_machine = OrderStateMachine(session)
        
        # Process event based on type and success
        if event_type == "stock_verified" and success:
            state_machine.transition_to(saga_id, OrderState.STOCK_VERIFIED)
            state_machine.log_step_completed(saga_id, "stock_verification", data)
            
        elif event_type == "stock_reserved" and success:
            state_machine.transition_to(saga_id, OrderState.STOCK_RESERVED)
            state_machine.log_step_completed(saga_id, "stock_reservation", data)
            
        elif event_type == "payment_processed" and success:
            state_machine.transition_to(saga_id, OrderState.PAYMENT_PROCESSED)
            state_machine.log_step_completed(saga_id, "payment_processing", data)
            
        elif not success:
            # Handle failure events
            state_machine.transition_to(saga_id, OrderState.COMPENSATION_STARTED)
            state_machine.log_step_failed(saga_id, f"{service}_{event_type}", data.get("error", "Unknown error"))
            
            # Trigger compensation
            trigger_compensation(saga_id, state_machine)
        
        session.close()
        
        return {"status": "event_processed", "saga_id": saga_id}
        
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8005)