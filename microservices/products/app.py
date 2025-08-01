from fastapi import FastAPI, HTTPException, Depends
from service import ProductService
from models.product_model import Product 
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List


app = FastAPI()
engine = create_engine("postgresql+psycopg2://admin:admin@db_products:5432/postgres")
Session = sessionmaker(bind=engine)
session = Session()

class ProductSerializer(BaseModel):
    id: int
    name: str
    category: str
    description: str
    prix_unitaire: float


class ProductCreateSerializer(BaseModel):
    name: str
    category: str
    description: str
    prix_unitaire: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the Products API"}

@app.get("/api/v1/products", response_model=List[ProductSerializer])
def get_all_products():
    service = ProductService(session)
    products = service.get_all_products() or []
    return products

@app.get("/api/v1/products/{product_id}", response_model=ProductSerializer)
def get_product_by_id(product_id: int):
    service = ProductService(session)
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product

@app.get("/api/v1/products/category/{category}", response_model=List[ProductSerializer])
def product_by_category(category: str):
    service = ProductService(session)
    products = service.get_product_by_category(category) or []
    return products

@app.post("/api/v1/products", response_model=ProductSerializer)
def add_product(product_data: ProductCreateSerializer):
    service = ProductService(session)
    # Convert Pydantic model to dict, then to SQLAlchemy model
    product_dict = product_data.dict()
    product = service.add_product(Product(**product_dict))
    return product

@app.put("/api/v1/products/{product_id}", response_model=ProductSerializer)
def update_product(
    product_id: int, 
    product_data: ProductCreateSerializer, 
):
    service = ProductService(session)
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Update product with new data
    product_dict = product_data.dict()
    updated_product = service.update_product(Product(**product_dict))
    return updated_product

@app.delete("/api/v1/products/{product_id}")
def delete_product(product_id: int):
    service = ProductService(session)
    deleted_product = service.delete_product(product_id)
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Not found")
    return {"detail": "Deleted successfully"}
