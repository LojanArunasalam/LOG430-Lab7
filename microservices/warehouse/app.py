from fastapi import FastAPI, HTTPException, Depends
from service import StoreService, StockService, ProductDepotService
from models.store_model import Store
from models.stock_model import Stock
from models.product_depot_model import Product_Depot
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional

import requests 
import logging

app = FastAPI(title="Warehouse Management Service")
engine = create_engine("postgresql+psycopg2://admin:admin@db_warehouse:5432/postgres")
Session = sessionmaker(bind=engine)

class StoreSerializer(BaseModel):
    id: int
    name: str

class StoreCreateSerializer(BaseModel):
    name: str

class StockSerializer(BaseModel):
    id: int
    product: int
    store: int
    quantite: int

class StockCreateSerializer(BaseModel):
    product: int
    store: int
    quantite: int

class StockUpdateSerializer(BaseModel):
    quantite: int

class ProductDepotSerializer(BaseModel):
    id: int
    product: int
    quantite_depot: int

class ProductDepotCreateSerializer(BaseModel):
    product: int
    quantite_depot: int

class TransferRequestSerializer(BaseModel):
    product: int
    store: int
    quantity: int

@app.get("/")
def read_root():
    return {"message": "Welcome to the Warehouse"}

# Store Endpoints
@app.get("/api/v1/stores", response_model=List[StoreSerializer])
def get_all_stores():
    session = Session()
    try:
        store_service = StoreService(session)
        stores = store_service.get_all_stores() or []
        return stores
    finally:
        session.close()

@app.get("/api/v1/stores/{store}", response_model=StoreSerializer)
def get_store_by_id(store: int):
    session = Session()
    try:
        store_service = StoreService(session)
        store = store_service.get_store_by_id(store)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        return store
    finally:
        session.close()

@app.post("/api/v1/stores", response_model=StoreSerializer)
def create_store(store_data: StoreCreateSerializer):
    session = Session()
    try:
        store_service = StoreService(session)
        store_dict = store_data.dict()
        store = store_service.add_store(Store(**store_dict))
        return store
    finally:
        session.close()

@app.put("/api/v1/stores/{store}", response_model=StoreSerializer)
def update_store(store: int, store_data: StoreCreateSerializer):
    session = Session()
    try:
        store_service = StoreService(session)
        existing_store = store_service.get_store_by_id(store)
        if not existing_store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Update fields
        update_data = store_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_store, field, value)
        
        updated_store = store_service.update_store(existing_store)
        return updated_store
    finally:
        session.close()

@app.delete("/api/v1/stores/{store}")
def delete_store(store: int):
    session = Session()
    try:
        store_service = StoreService(session)
        deleted_store = store_service.delete_store(store)
        if not deleted_store:
            raise HTTPException(status_code=404, detail="Store not found")
        return {"detail": "Store deleted successfully"}
    finally:
        session.close()

# Stock Endpoints
@app.get("/api/v1/stocks", response_model=List[StockSerializer])
def get_all_stocks():
    session = Session()
    try:
        stock_service = StockService(session)
        stocks = stock_service.get_all_stocks() or []
        return stocks
    finally:
        session.close()

@app.get("/api/v1/stocks/{stock_id}", response_model=StockSerializer)
def get_stock_by_id(stock_id: int):
    session = Session()
    try:
        stock_service = StockService(session)
        stock = stock_service.get_stock_by_id(stock_id)
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        return stock
    finally:
        session.close()

@app.get("/api/v1/stocks/product/{product}/store/{store}", response_model=StockSerializer)
def get_stock_by_product_and_store(product: int, store: int):
    session = Session()
    try:
        stock_service = StockService(session)
        stock = stock_service.get_stock_by_product_and_store(product, store)
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        return stock
    finally:
        session.close()

@app.get("/api/v1/stocks/store/{store}", response_model=List[StockSerializer])
def get_stocks_by_store(store: int):
    session = Session()
    try:
        stock_service = StockService(session)
        stocks = stock_service.get_stocks_by_store(store) or []
        return stocks
    finally:
        session.close()

@app.get("/api/v1/stocks/product/{product}", response_model=List[StockSerializer])
def get_stocks_by_product(product: int):
    session = Session()
    try:
        stock_service = StockService(session)
        stocks = stock_service.get_stocks_by_product(product) or []
        return stocks
    finally:
        session.close()

@app.post("/api/v1/stocks", response_model=StockSerializer)
def create_stock(stock_data: StockCreateSerializer):
    session = Session()
    try:
        stock_service = StockService(session)
        stock_dict = stock_data.dict()
        stock = stock_service.add_stock(Stock(**stock_dict))
        return stock
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

@app.put("/api/v1/stocks/product/{product}/store/{store}", response_model=StockSerializer)
def update_stock_quantity(product: int, store: int, stock_data: StockUpdateSerializer):
    session = Session()
    try:
        stock_service = StockService(session)
        updated_stock = stock_service.update_stock_quantity(product, store, stock_data.quantite)
        return updated_stock
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

@app.post("/api/v1/stocks/reduce")
def reduce_stock(product: int, store: int, quantity: int, saga_id: Optional[int] = None):
    session = Session()
    try:
        stock_service = StockService(session)
        reduced_stock = stock_service.reduce_stock(product, store, quantity)

        if saga_id and reduced_stock:
            publish_event(event_type="stock_reserved", saga_id=saga_id, data={
                "product_id": product,
                "store_id": store,
                "quantity": quantity,
                "new_quantity": reduced_stock.quantite
            }, success=True)
        
        return {
            "message": "Stock reduced successfully",
            "new_quantity": reduced_stock.quantite
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

@app.post("/api/v1/stocks/increase")
def increase_stock(product: int, store: int, quantity: int):
    session = Session()
    try:
        stock_service = StockService(session)
        increased_stock = stock_service.increase_stock(product, store, quantity)
        return {
            "message": "Stock increased successfully", 
            "new_quantity": increased_stock.quantite
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

@app.delete("/api/v1/stocks/{stock_id}")
def delete_stock(stock_id: int):
    session = Session()
    try:
        stock_service = StockService(session)
        deleted_stock = stock_service.delete_stock(stock_id)
        if not deleted_stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        return {"detail": "Stock deleted successfully"}
    finally:
        session.close()

# Product Depot Endpoints
@app.get("/api/v1/depot", response_model=List[ProductDepotSerializer])
def get_all_depot_stocks():
    session = Session()
    try:
        depot_service = ProductDepotService(session)
        depots = depot_service.get_all_depot_stocks() or []
        return depots
    finally:
        session.close()

@app.get("/api/v1/depot/{depot_id}", response_model=ProductDepotSerializer)
def get_depot_by_id(depot_id: int):
    session = Session()
    try:
        depot_service = ProductDepotService(session)
        depot = depot_service.get_depot_by_id(depot_id)
        if not depot:
            raise HTTPException(status_code=404, detail="Depot stock not found")
        return depot
    finally:
        session.close()

@app.get("/api/v1/depot/product/{product}", response_model=ProductDepotSerializer)
def get_depot_by_product(product: int):
    session = Session()
    try:
        depot_service = ProductDepotService(session)
        depot = depot_service.get_depot_by_product_id(product)
        if not depot:
            raise HTTPException(status_code=404, detail="Depot stock not found for this product")
        return depot
    finally:
        session.close()

@app.post("/api/v1/depot", response_model=ProductDepotSerializer)
def create_depot_stock(depot_data: ProductDepotCreateSerializer):
    session = Session()
    try:
        depot_service = ProductDepotService(session)
        depot_dict = depot_data.dict()
        depot = depot_service.add_depot_stock(Product_Depot(**depot_dict))
        return depot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

@app.post("/api/v1/depot/transfer", response_model=dict)
def transfer_from_depot_to_store(transfer_data: TransferRequestSerializer):
    """Transfer stock from depot to store"""
    session = Session()
    try:
        depot_service = ProductDepotService(session)
        result = depot_service.transfer_to_store(
            transfer_data.product,
            transfer_data.store,
            transfer_data.quantity
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()

def publish_event(event_type: str, saga_id: int, data: dict, success: bool = True):
    """Publish event to saga orchestrator"""
    try:
        event_payload = {
            "saga_id": saga_id,
            "event_type": event_type,
            "success": success,
            "data": data,
            "service": "warehouse"
        }
        
        response = requests.post(
            "http://saga_orchestrator:8005/api/v1/saga/events",
            json=event_payload
        )
        
        if response.status_code != 200:
            logging.error(f"Failed to publish event: {response.text}")
    except Exception as e:
        logging.error(f"Error publishing event: {e}")

# # Warehouse Complex Operations
# @app.get("/api/v1/inventory/product/{product}")
# def get_complete_inventory_info(product: int, store: Optional[int] = None):
#     """Get comprehensive inventory information for a product"""
#     session = Session()
#     try:
#         warehouse_service = WarehouseService(session)
#         inventory_info = warehouse_service.get_complete_inventory_info(product, store)
#         if not inventory_info:
#             raise HTTPException(status_code=404, detail="Inventory information not found")
#         return inventory_info
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     finally:
#         session.close()

# @app.get("/api/v1/alerts/low-stock")
# def get_low_stock_alerts(minimum_threshold: int = 5):
#     """Get products with low stock across all stores"""
#     session = Session()
#     try:
#         warehouse_service = WarehouseService(session)
#         low_stock_items = warehouse_service.get_low_stock_alerts(minimum_threshold)
#         return {
#             "threshold": minimum_threshold,
#             "low_stock_items": low_stock_items,
#             "count": len(low_stock_items)
#         }
#     finally:
#         session.close()

# @app.post("/api/v1/restock")
# def restock_store_from_depot(transfer_data: TransferRequestSerializer):
#     """Restock a store from depot"""
#     session = Session()
#     try:
#         warehouse_service = WarehouseService(session)
#         result = warehouse_service.restock_store_from_depot(
#             transfer_data.product,
#             transfer_data.store,
#             transfer_data.quantity
#         )
#         return result
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     finally:
#         session.close()