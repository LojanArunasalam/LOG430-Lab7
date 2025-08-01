from rest_framework.response import Response
from rest_framework.decorators import api_view
from caisse.services.product_service import ProductService
from api.serializers import ProductSerializer
from caisse.models import engine, Product
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

@api_view(['GET'])
def get_all_products(request):
    session = Session()
    service = ProductService(session)
    products = service.get_all_products() or []
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_product_by_id(request, id):
    session = Session()
    service = ProductService(session)
    product = service.get_product_by_id(id)
    if not product:
        return Response({'detail': 'Not found.'}, status=404)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
def product_by_category(request, category):
    session = Session()
    service = ProductService(session)
    products = service.get_product_by_category(category) or []
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_product(request):
    session = Session()
    service = ProductService(session)
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = service.add_product(Product(**serializer.validated_data))
        return Response(ProductSerializer(product).data)
    return Response(serializer.errors)

@api_view(['PUT'])
def update_product(request, pk):
    session = Session()
    service = ProductService(session)
    product = service.get_product_by_id(pk)
    if not product:
        return Response({'detail': 'Not found.'})
    serializer = ProductSerializer(product, data=request.data)
    if serializer.is_valid():
        updated_product = service.update_product(Product(**serializer.validated_data))
        return Response(ProductSerializer(updated_product).data)
    return Response(serializer.errors)

@api_view(['DELETE'])
def delete_product(request, pk):
    session = Session()
    service = ProductService(session)
    deleted_product = service.delete_product(pk)
    if not deleted_product:
        return Response({'detail': 'Not found.'})
    return Response({'detail': 'Deleted successfully.'})