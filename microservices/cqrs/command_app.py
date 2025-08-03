# CQRS Command Service - FastAPI Application

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import asyncio
import sys
import os

# Add shared events to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.events.publisher import EventPublisher
from models import (
    CreateOrderCommand, ProcessPaymentCommand, UpdateInventoryCommand,
    CreateOrderCommandHandler, ProcessPaymentCommandHandler
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CQRS Command Service", version="1.0.0")

# Global instances
event_publisher = None
command_handlers = {}

# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

class CreateOrderRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class ProcessPaymentRequest(BaseModel):
    order_id: str
    amount: float
    payment_method: str

class UpdateInventoryRequest(BaseModel):
    product_id: int
    quantity_change: int
    operation: str  # 'reserve', 'release', 'deduct', 'restock'

class CommandResponse(BaseModel):
    success: bool
    command_id: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize command service"""
    global event_publisher, command_handlers
    
    try:
        # Initialize event publisher
        event_publisher = EventPublisher()
        
        # Initialize command handlers
        command_handlers = {
            "CreateOrder": CreateOrderCommandHandler(event_publisher),
            "ProcessPayment": ProcessPaymentCommandHandler(event_publisher)
        }
        
        logger.info("CQRS Command Service started successfully")
        
    except Exception as e:
        logger.error(f"Error starting CQRS Command Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup command service"""
    global event_publisher
    
    try:
        if event_publisher:
            await event_publisher.close()
        
        logger.info("CQRS Command Service shut down successfully")
        
    except Exception as e:
        logger.error(f"Error shutting down CQRS Command Service: {e}")

# ============================================================================
# COMMAND ENDPOINTS
# ============================================================================

@app.post("/commands/orders", response_model=CommandResponse)
async def create_order(request: CreateOrderRequest, background_tasks: BackgroundTasks):
    """Create a new order"""
    try:
        # Create command
        command = CreateOrderCommand(
            user_id=request.user_id,
            product_id=request.product_id,
            quantity=request.quantity
        )
        
        # Handle command
        handler = command_handlers["CreateOrder"]
        result = await handler.handle(command)
        
        return CommandResponse(
            success=result["success"],
            command_id=result["command_id"],
            message=result.get("message", ""),
            data={"order_id": result.get("order_id")} if result["success"] else None,
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/commands/payments", response_model=CommandResponse)
async def process_payment(request: ProcessPaymentRequest, background_tasks: BackgroundTasks):
    """Process a payment"""
    try:
        # Create command
        command = ProcessPaymentCommand(
            order_id=request.order_id,
            amount=request.amount,
            payment_method=request.payment_method
        )
        
        # Handle command
        handler = command_handlers["ProcessPayment"]
        result = await handler.handle(command)
        
        return CommandResponse(
            success=result["success"],
            command_id=result["command_id"],
            message=result.get("message", ""),
            data={"payment_id": result.get("payment_id")} if result["success"] else None,
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/commands/inventory", response_model=CommandResponse)
async def update_inventory(request: UpdateInventoryRequest, background_tasks: BackgroundTasks):
    """Update inventory (reserve, release, deduct, restock)"""
    try:
        # Create command
        command = UpdateInventoryCommand(
            product_id=request.product_id,
            quantity_change=request.quantity_change,
            operation=request.operation
        )
        
        # For inventory commands, we publish events directly since they're simpler
        event_data = {
            "product_id": command.product_id,
            "quantity": command.quantity_change,
            "operation": command.operation,
            "command_id": command.command_id
        }
        
        # Determine event type based on operation
        event_type_map = {
            "reserve": "InventoryReserveRequested",
            "release": "InventoryReleaseRequested", 
            "deduct": "InventoryDeductRequested",
            "restock": "InventoryRestockRequested"
        }
        
        event_type = event_type_map.get(command.operation, "InventoryUpdateRequested")
        
        # Publish event
        event_publisher.publish_event(
            event_type=event_type,
            aggregate_type="inventory",
            aggregate_id=str(command.product_id),
            data=event_data,
            service_name="cqrs-command"
        )
        
        return CommandResponse(
            success=True,
            command_id=command.command_id,
            message=f"Inventory {command.operation} requested",
            data={"product_id": command.product_id, "operation": command.operation}
        )
        
    except Exception as e:
        logger.error(f"Error updating inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "cqrs-command",
        "timestamp": datetime.utcnow().isoformat(),
        "handlers": list(command_handlers.keys())
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "CQRS Command Service",
        "description": "Handles write operations (commands) in the CQRS pattern",
        "version": "1.0.0",
        "endpoints": {
            "POST /commands/orders": "Create new order",
            "POST /commands/payments": "Process payment",
            "POST /commands/inventory": "Update inventory",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
