from rest_framework.response import Response
from rest_framework.decorators import api_view
from caisse.services.stock_service import StockService
from api.serializers import StockSerializer
from caisse.models import engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

@api_view(['GET'])
def get_all_stocks(request):
    session = Session()
    service = StockService(session)
    sales = service.get_all_stocks() or []
    serializer = StockSerializer(sales, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_stocks_by_id(request, id):
    session = Session()
    service = StockService(session)
    stock = service.get_stock_by_id(id) or []
    serializer = StockSerializer(stock, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def get_stocks_by_store(request, store_id):
    session = Session()
    service = StockService(session)
    sales = service.get_stock_by_store(store_id) or []
    serializer = StockSerializer(sales, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_stocks_by_store_and_product(request, product_id, store_id):
    session = Session()
    service = StockService(session)
    sales = service.get_stock_by_product_and_store(product_id, store_id) or []
    serializer = StockSerializer(sales, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def update_stock(request, pk):
    session = Session()
    service = StockService(session)
    stock = service.get_stock_by_id(pk)
    if not stock:
        return Response({'detail': 'Not found.'}, status=404)
    serializer = StockSerializer(stock, data=request.data)
    if serializer.is_valid():
        updated_stock = service.update_stock(stock)
        return Response(StockSerializer(updated_stock).data)
    return Response(serializer.errors)

@api_view(['DELETE'])
def delete_stock(request, pk):
    session = Session()
    service = StockService(session)
    deleted = service.delete_stock(pk)
    if not deleted:
        return Response({'detail': 'Not found.'}, status=404)
    return Response({'detail': 'Deleted successfully.'})