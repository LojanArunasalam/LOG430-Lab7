from .models import Product, Stock, Sale, LineSale, Store, User, Product_Depot, engine
from caisse.services.caisse_service import CaisseService
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

class Caisse:
    def __init__(self, store_id):
        self.store_id = store_id
        self.caisse_service = CaisseService(session)
        
    def enregistrer_vente(self, product_id):
        self.caisse_service.enregistrer_vente(product_id, self.store_id)

    def enregistrer_ligne_vente(self, product_id, quantite):
        self.caisse_service.enregistrer_ligne_vente(product_id, self.store_id)
        

    def update_stock(self, product_id, quantite):
        self.caisse_service.update_stock(product_id, quantite, self.store_id)
