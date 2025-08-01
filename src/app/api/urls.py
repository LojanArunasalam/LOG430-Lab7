from django.urls import path
from . import product_views, sale_views, domain_views, stock_views, caisse_views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Caisse API",
        default_version='v1',
        description="API for managing sales, products, stocks, and more.",
    ),
    public=True,
)

urlpatterns = [
    # Products routes
    path('api/v1/products/', product_views.get_all_products),
    path('api/v1/products/<int:id>/', product_views.get_product_by_id),
    path('api/v1/products/category/<str:category>/', product_views.product_by_category),
    path('api/v1/products/add/', product_views.add_product),
    path('api/v1/products/del/<int:id>/', product_views.delete_product),

    # Sales routes
    path('api/v1/sales/', sale_views.get_all_sales),
    path('api/v1/sales/<int:store_id>/', sale_views.get_sales_by_store),
    path('api/v1/sales/user/<int:user_id>/', sale_views.get_sales_by_user),
    path('api/v1/sales/update/', sale_views.update_sale),
    path('api/v1/sales/del/<int:id>', sale_views.delete_sale),

    # Stock routes
    path('api/v1/stocks/', stock_views.get_all_stocks),
    path('api/v1/stocks/<int:id>/', stock_views.get_stocks_by_id),
    path('api/v1/stocks/store/<int:id>/', stock_views.get_stocks_by_store),
    path('api/v1/stocks/store/<int:store_id>/product/<int:product_id>/', stock_views.get_stocks_by_store_and_product),
    path('api/v1/stocks/update/', stock_views.update_stock),
    path('api/v1/stocks/del/<int:id>/', stock_views.delete_stock),
    
    # Product_Depot routes

    # LineSales routes

    # Stores routes

    # Performances routes
    path('api/v1/performances/', domain_views.performances),
    # Report routes
    path('api/v1/report/<int:store_id>', domain_views.report),

    # Caisser routes
    path('api/v1/caisse/<int:store_id>', caisse_views.enregistrer_vente),
    path('api/v1/caisse/ligne/<int:store_id>', caisse_views.enregistrer_ligne_vente),

    path('api/v1/swagger/schema', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),


]
