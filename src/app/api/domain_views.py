from rest_framework.response import Response
from rest_framework.decorators import api_view
from caisse.services.domain_service import DomainService 
from caisse.models import engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)


@api_view(['GET'])
def performances(request):
    session = Session()
    service = DomainService(session)
    performances_data = service.performances()
# Convert generator/zip to list of dicts for JSON
    result = []
    for total, stocks, store_id in performances_data:
        result.append({
            'store_id': store_id,
            'total_sales': total,
            'stocks': [
                {'product_id': stock.product, 'quantity': stock.quantite} for stock in stocks
            ] if stocks else []
        })
    return Response(result)

@api_view(['GET'])
def report(request, store_id):
    session = Session()
    service = DomainService(session)
    report = service.generate_report(store_id)
    # You may want to serialize sales and most_sold_product if needed
    # For now, just convert to dict with IDs and values
    report_data = {
        'store_id': report['store_id'],
        'sales': [sale.id for sale in report['sales']],
        'most_sold_product': getattr(report['most_sold_product'], 'id', None) if report['most_sold_product'] else None,
        'max_quantity': report['max_quantity']
    }
    return Response(report_data)