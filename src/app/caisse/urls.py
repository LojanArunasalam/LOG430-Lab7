from django.urls import path 
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("report/<int:store_id>", views.report, name="report"),
    path("products/", views.search_products, name="products"),
    path("stock-central/", views.dashboard_logistique, name="stock-central"),
    path('restock/<int:product_id>/<int:store_id>/', views.restock_product, name='restock_product'),
    path("performances/", views.performances, name="performances"),
    path("buy-product/<int:product_id>/<int:store_id>/", views.buy_product, name="buy_product"),
]