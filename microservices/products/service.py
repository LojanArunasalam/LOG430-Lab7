from repository import ProductRepository
import logging 
class ProductService: 
    def __init__(self, session):
        self.session = session
        self.product_repository = ProductRepository(session)

    def get_product_by_id(self, id):
        product = self.product_repository.get_by_id(id)
        return product
    
    def get_all_products(self):
        products = self.product_repository.get_all_products()
        return products

    def get_product_by_category(self, category):
        products = self.product_repository.get_product_by_category(category)
        return products

    def add_product(self, product):
        self.product_repository.add_product(product)
        return product
    
    def update_product(self, product):
        updated_product = self.product_repository.update_product(product)
        return updated_product
    
    def delete_product(self, product_id):
        deleted_product = self.product_repository.delete_product(product_id)
        return deleted_product


