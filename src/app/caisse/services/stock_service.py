from caisse.repositories.stock_repository import StockRepository

class StockService: 
    def __init__(self, session):
        self.session = session
        self.stock_repository = StockRepository(session)

    def get_stock_by_id(self, id):
        return self.stock_repository.get_by_id(self.session, id)

    def get_all_stocks(self):
        return self.stock_repository.get_all_stocks(self.session)

    def get_stock_by_store(self, store_id):
        return self.stock_repository.get_stock_by_store(self.session, store_id)

    def get_stock_by_product_and_store(self, product_id, store_id):
        return self.stock_repository.get_stock_by_product_and_store(self.session, product_id, store_id)
    
    
    def delete_stock(self, stock_id):
        stock = self.stock_repository.get_by_id(self.session, stock_id)
        if stock:
            self.session.delete(stock)
            self.session.commit()
            return True
        return False


