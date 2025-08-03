# CQRS Query Service - FastAPI Application

from fastapi import FastAPI, HTTPException, Query as FastAPIQuery
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import asyncio
import sys
import os

# Add shared events to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from read_store import CQRSReadStore
from models import (
    GetOrderQuery, GetUserOrdersQuery, GetInventoryQuery, GetOrderStatisticsQuery,
    GetOrderQueryHandler, GetUserOrdersQueryHandler, GetInventoryQueryHandler
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CQRS Query Service", version="1.0.0")

# Global instances
read_store = None
query_handlers = {}

# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

class QueryResponse(BaseModel):
    success: bool
    query_id: str
    data: Optional[Any] = None
    count: Optional[int] = None
    error: Optional[str] = None

class OrderSummary(BaseModel):
    order_id: str
    user_id: int
    user_email: str
    total_amount: float
    status: str
    created_at: Optional[str]

class InventorySummary(BaseModel):
    product_id: int
    product_name: str
    available_quantity: int
    reserved_quantity: int
    low_stock_alert: bool

class UserOrderSummary(BaseModel):
    user_id: int
    user_email: str
    total_orders: int
    total_spent: float
    avg_order_value: float

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize query service"""
    global read_store, query_handlers
    
    try:
        # Initialize read store
        read_store = CQRSReadStore()
        await read_store.connect()
        
        # Initialize query handlers
        query_handlers = {
            "GetOrder": GetOrderQueryHandler(read_store),
            "GetUserOrders": GetUserOrdersQueryHandler(read_store),
            "GetInventory": GetInventoryQueryHandler(read_store)
        }
        
        logger.info("CQRS Query Service started successfully")
        
    except Exception as e:
        logger.error(f"Error starting CQRS Query Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup query service"""
    global read_store
    
    try:
        if read_store:
            await read_store.disconnect()
        
        logger.info("CQRS Query Service shut down successfully")
        
    except Exception as e:
        logger.error(f"Error shutting down CQRS Query Service: {e}")

# ============================================================================
# QUERY ENDPOINTS
# ============================================================================

@app.get("/queries/orders/{order_id}", response_model=QueryResponse)
async def get_order(order_id: str):
    """Get order details by ID"""
    try:
        # Create query
        query = GetOrderQuery(order_id=order_id)
        
        # Handle query
        handler = query_handlers["GetOrder"]
        result = await handler.handle(query)
        
        return QueryResponse(
            success=result["success"],
            query_id=result["query_id"],
            data=result.get("data"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/users/{user_id}/orders", response_model=QueryResponse)
async def get_user_orders(
    user_id: int, 
    status: Optional[str] = FastAPIQuery(None, description="Filter by order status")
):
    """Get orders for a specific user"""
    try:
        # Create query
        query = GetUserOrdersQuery(user_id=user_id, status=status)
        
        # Handle query
        handler = query_handlers["GetUserOrders"]
        result = await handler.handle(query)
        
        return QueryResponse(
            success=result["success"],
            query_id=result["query_id"],
            data=result.get("data"),
            count=result.get("count"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error getting orders for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/inventory", response_model=QueryResponse)
async def get_all_inventory():
    """Get all inventory items"""
    try:
        # Create query
        query = GetInventoryQuery()
        
        # Handle query
        handler = query_handlers["GetInventory"]
        result = await handler.handle(query)
        
        return QueryResponse(
            success=result["success"],
            query_id=result["query_id"],
            data=result.get("data"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/inventory/{product_id}", response_model=QueryResponse)
async def get_product_inventory(product_id: int):
    """Get inventory for a specific product"""
    try:
        # Create query
        query = GetInventoryQuery(product_id=product_id)
        
        # Handle query
        handler = query_handlers["GetInventory"]
        result = await handler.handle(query)
        
        return QueryResponse(
            success=result["success"],
            query_id=result["query_id"],
            data=result.get("data"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error getting inventory for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/inventory/low-stock", response_model=QueryResponse)
async def get_low_stock_items():
    """Get items with low stock"""
    try:
        inventories = await read_store.get_low_stock_items()
        
        return QueryResponse(
            success=True,
            query_id="low-stock-query",
            data=[inv.to_dict() for inv in inventories],
            count=len(inventories)
        )
        
    except Exception as e:
        logger.error(f"Error getting low stock items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/orders/recent", response_model=QueryResponse)
async def get_recent_orders(limit: int = FastAPIQuery(50, ge=1, le=200)):
    """Get recent orders"""
    try:
        orders = await read_store.get_recent_orders(limit)
        
        return QueryResponse(
            success=True,
            query_id="recent-orders-query",
            data=[order.to_dict() for order in orders],
            count=len(orders)
        )
        
    except Exception as e:
        logger.error(f"Error getting recent orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/orders/status/{status}", response_model=QueryResponse)
async def get_orders_by_status(status: str):
    """Get orders by status"""
    try:
        orders = await read_store.get_orders_by_status(status.upper())
        
        return QueryResponse(
            success=True,
            query_id=f"orders-by-status-{status}",
            data=[order.to_dict() for order in orders],
            count=len(orders)
        )
        
    except Exception as e:
        logger.error(f"Error getting orders by status {status}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/users/{user_id}/summary", response_model=QueryResponse)
async def get_user_summary(user_id: int):
    """Get user order summary"""
    try:
        summary = await read_store.get_user_summary(user_id)
        
        if summary:
            return QueryResponse(
                success=True,
                query_id=f"user-summary-{user_id}",
                data=summary.to_dict()
            )
        else:
            return QueryResponse(
                success=False,
                query_id=f"user-summary-{user_id}",
                error="User summary not found"
            )
        
    except Exception as e:
        logger.error(f"Error getting user summary for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/customers/top", response_model=QueryResponse)
async def get_top_customers(limit: int = FastAPIQuery(10, ge=1, le=100)):
    """Get top customers by total spent"""
    try:
        customers = await read_store.get_top_customers(limit)
        
        return QueryResponse(
            success=True,
            query_id="top-customers-query",
            data=[customer.to_dict() for customer in customers],
            count=len(customers)
        )
        
    except Exception as e:
        logger.error(f"Error getting top customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queries/statistics/orders", response_model=QueryResponse)
async def get_order_statistics(
    start_date: Optional[str] = FastAPIQuery(None, description="Start date (ISO format)"),
    end_date: Optional[str] = FastAPIQuery(None, description="End date (ISO format)")
):
    """Get order statistics for a date range"""
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Create query
        query = GetOrderStatisticsQuery(start_date=start_dt, end_date=end_dt)
        
        # Get statistics
        stats = await read_store.get_order_statistics(start_dt, end_dt)
        
        return QueryResponse(
            success=True,
            query_id=query.query_id,
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting order statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "cqrs-query",
        "timestamp": datetime.utcnow().isoformat(),
        "handlers": list(query_handlers.keys())
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "CQRS Query Service",
        "description": "Handles read operations (queries) in the CQRS pattern",
        "version": "1.0.0",
        "endpoints": {
            "GET /queries/orders/{order_id}": "Get order details",
            "GET /queries/users/{user_id}/orders": "Get user orders",
            "GET /queries/inventory": "Get all inventory",
            "GET /queries/inventory/{product_id}": "Get product inventory",
            "GET /queries/inventory/low-stock": "Get low stock items",
            "GET /queries/orders/recent": "Get recent orders",
            "GET /queries/orders/status/{status}": "Get orders by status",
            "GET /queries/users/{user_id}/summary": "Get user summary",
            "GET /queries/customers/top": "Get top customers",
            "GET /queries/statistics/orders": "Get order statistics",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
