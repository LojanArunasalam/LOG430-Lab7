from rest_framework.response import Response
from rest_framework.decorators import api_view
from caisse.services.sale_service import SaleService
from api.serializers import SaleSerializer
from caisse.models import engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

@api_view(['GET'])
def get_all_sales(request):
    session = Session()
    service = SaleService(session)
    sales = service.get_all_sales() or []
    serializer = SaleSerializer(sales, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_sales_by_store(request, store_id):
    session = Session()
    service = SaleService(session)
    sales = service.get_sales_by_store(store_id) or []
    serializer = SaleSerializer(sales, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_sales_by_user(request, user_id):
    session = Session()
    service = SaleService(session)
    sales = service.get_sales_by_user(user_id) or []
    serializer = SaleSerializer(sales, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def update_sale(request, pk):
    session = Session()
    service = SaleService(session)
    sale = service.sale_repository.get_by_id(pk)
    if not sale:
        return Response({'detail': 'Not found.'}, status=404)
    serializer = SaleSerializer(sale, data=request.data)
    if serializer.is_valid():
        updated_sale = service.update_sale(sale)
        return Response(SaleSerializer(updated_sale).data)
    return Response(serializer.errors)

@api_view(['DELETE'])
def delete_sale(request, pk):
    session = Session()
    service = SaleService(session)
    deleted = service.delete_sale(pk)
    if not deleted:
        return Response({'detail': 'Not found.'}, status=404)
    return Response({'detail': 'Deleted successfully.'})
