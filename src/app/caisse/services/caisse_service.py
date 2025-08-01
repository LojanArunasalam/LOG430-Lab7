import logging
from ..models import Product, LineSale, Sale
from ..repositories.product_repository import ProductRepository
from ..repositories.sale_repository import SaleRepository
from ..repositories.stock_repository import StockRepository

class CaisseService:
    def __init__(self, session):
        self.session = session
        self.productRepository = ProductRepository(session)
        self.saleRepository = SaleRepository(session)
        self.stockRepository = StockRepository(session)
        
    def enregistrer_ligne_vente(self, product_id, quantite):
        product = self.productRepository.get_by_id(product_id)
        ligne_vente = LineSale(product=product_id, quantite=quantite, prix=product.prix_unitaire)
        return ligne_vente

    def enregistrer_vente(self, product_id, store_id):
        lignes_ventes = []
        product = self.productRepository.get_by_id(product_id)
        stock = self.stockRepository.get_stock_by_product_and_store(self.session, product.id, store_id)

        if stock.quantite - 1 < 0:
            raise Exception("Stock insuffisant pour ce produit")

        self.update_stock(product_id, 1, store_id)
        ligne_vente = self.enregistrer_ligne_vente(product_id, 1)
        lignes_ventes.append(ligne_vente)

        total = sum(line.prix for line in lignes_ventes)

        sale = Sale(line_vente=lignes_ventes, total=total, store=store_id)
        self.saleRepository.add_sale(sale)

    def update_stock(self, product_id, quantite, store_id):
        stock = self.stockRepository.get_stock_by_product_and_store(self.session, product_id, store_id)
        stock.quantite -= quantite
        self.session.add(stock)
        self.session.commit()