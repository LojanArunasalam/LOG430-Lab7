from caisse.repositories.sale_repository import SaleRepository
from ..models import LineSale, Sale

class SaleService: 
    def __init__(self, session):
        self.session = session
        self.sale_repository = SaleRepository(session)
        
    def get_all_sales(self):
        sales = self.sale_repository.get_all_sales()
        return sales
    
    def get_sales_by_store(self, store_id):
        sales = self.sale_repository.get_sales_by_store(store_id)
        return sales
    
    def get_sales_by_user(self, user_id):
        sales = self.sale_repository.get_sales_by_user(user_id)
        return sales
    
    def update_sale(self, sale):
        self.session.add(sale)
        self.session.commit()
        return sale
    
    def delete_sale(self, sale_id):
        sale = self.sale_repository.get_by_id(sale_id)
        if sale:
            self.session.delete(sale)
            self.session.commit()
            return True
        return False
    
    
    
        
