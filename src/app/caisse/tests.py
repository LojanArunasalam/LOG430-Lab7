from django.test import TestCase
import pytest 
from caisse.models import Product, Sale, LineSale, User, Store, Product_Depot, Stock

# Create your tests here.

def test_product():
    product = Product(
        name="Timbits",
        category="Snacks",
        description="Tiny donut balls",
        prix_unitaire=0.25,
    )
    assert product.name == "Timbits"
    assert product.prix_unitaire == pytest.approx(0.25)

def test_sale():
    sale = Sale(
        total = 10.00,
        user = 1,
        store = 1
    )
    assert sale.total == pytest.approx(10.00)
    assert sale.user == 1  
    assert sale.store == 1    

def test_line_sale():
    line_sale = LineSale(
        product=1,
        sale=1,
        quantite=5,
        prix=2.00
    )

    assert line_sale.product == 1
    assert line_sale.quantite == 5
    assert line_sale.prix == pytest.approx(2.00)
    

def test_store():
    store = Store(
        id=1,
        name="123 Main St"
    )

    assert store.id == 1

def test_product_depot():
    product_depot = Product_Depot(
        id=1,
        product=1,
        quantite_depot=100
    )

    assert product_depot.id == 1
    assert product_depot.product == 1
    assert product_depot.quantite_depot == 100



def test_stock():
    stock = Stock(
        id=1,
        product=1,
        store=1,
        quantite=50
    ) 

    assert stock.id == 1
    assert stock.product == 1
    assert stock.store == 1
    assert stock.quantite == 50



