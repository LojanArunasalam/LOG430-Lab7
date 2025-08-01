from fastapi import FastAPI, HTTPException, Depends
from service import UserService
from models.user_model import User 
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional

app = FastAPI(title="Customer/User Management Service")
engine = create_engine("postgresql+psycopg2://admin:admin@10.194.32.165:5435/postgres")
Session = sessionmaker(bind=engine)
session = Session()

class UserSerializer(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[str] = None

class UserCreateSerializer(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserUpdateSerializer(BaseModel): 
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the Customer Management API"}

@app.get("/api/v1/customers", response_model=List[UserSerializer])
def get_all_customers():
    service = UserService(session)
    users = service.get_all_users() or []
    return users

@app.get("/api/v1/customers/{customer_id}", response_model=UserSerializer)
def get_customer_by_id(customer_id: int):
    service = UserService(session)
    user = service.get_user_by_id(customer_id)
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    return user

@app.get("/api/v1/customers/email/{email}", response_model=UserSerializer)
def get_customer_by_email(email: str):
    service = UserService(session)
    user = service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    return user

@app.post("/api/v1/customers", response_model=UserSerializer)
def create_customer(user_data: UserCreateSerializer):
    service = UserService(session)
    try:
        # Convert Pydantic model to dict, then to SQLAlchemy model
        user_dict = user_data.dict()
        user = service.add_user(User(**user_dict))
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/v1/customers/{customer_id}", response_model=UserSerializer)
def update_customer(customer_id: int, user_data: UserUpdateSerializer):
    service = UserService(session)
    
    # Get existing user
    existing_user = service.get_user_by_id(customer_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Update only provided fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_user, field, value)
    
    updated_user = service.update_user(existing_user)
    return updated_user

@app.delete("/api/v1/customers/{customer_id}")
def delete_customer(customer_id: int):
    service = UserService(session)
    deleted_user = service.delete_user(customer_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"detail": "Customer deleted successfully"}

# Additional endpoint for customer account creation (specific requirement)
@app.post("/api/v1/accounts/register", response_model=UserSerializer)
def register_customer_account(user_data: UserCreateSerializer):
    """
    Specific endpoint for customer account creation as required
    """
    return create_customer(user_data) 