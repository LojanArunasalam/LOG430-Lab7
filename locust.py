import time
from locust import HttpUser, task, between
import random as rand

class MyUser(HttpUser):
    wait_time = between(1, 5)  # Wait time between tasks

    @task
    def products(self):
        # Simulate a user checking the products api
        self.client.get("/products/api/v1/products")

    @task 
    def product_details(self):
        # Simulate a user checking details of a specific product
        product_id = rand.randint(1, 5)  # Assuming product IDs are between 1 and 100
        self.client.get(f"/products/api/v1/products/{product_id}")
    
    @task
    def stocks(self):
        # Simulate a user checking the stocks api
        store = rand.choice([1, 2, 3, 4, 5])
        self.client.get(f"/warehouse/api/v1/stocks/store/{store}")

    @task
    def users(self):
        # Simulate a user checking the stocks api
        self.client.get(f"/users/api/v1/customers")
