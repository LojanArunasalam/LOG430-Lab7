from rest_framework import serializers
from caisse.models import Product, Sale, LineSale, Stock, User, Product_Depot, Store

class LineSaleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    quantite = serializers.IntegerField()
    prix = serializers.FloatField()
    sale = serializers.IntegerField()
    product = serializers.IntegerField()

class StockSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    quantite = serializers.IntegerField()
    product = serializers.IntegerField()
    store = serializers.IntegerField()

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    category = serializers.CharField()
    description = serializers.CharField()
    prix_unitaire = serializers.FloatField()
    # Optionally, you can add nested serializers for line_sale and stock if needed

class SaleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    total = serializers.FloatField()
    user = serializers.IntegerField()
    store = serializers.IntegerField()
    # Optionally, you can add nested LineSaleSerializer for line_vente

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    # Optionally, you can add nested SaleSerializer for sale

class ProductDepotSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    quantite_depot = serializers.IntegerField()
    product = serializers.IntegerField()

class StoreSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    # Optionally, you can add nested StockSerializer and SaleSerializer for stocks and sales