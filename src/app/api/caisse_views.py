from rest_framework.response import Response
from rest_framework.decorators import api_view
from caisse.caisse_controller import Caisse
from caisse.models import engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

@api_view(['POST'])
def enregistrer_vente(request, store_id):
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'detail': 'Missing product_id.'}, status=400)
    caisse = Caisse(store_id)
    try:
        caisse.enregistrer_vente(product_id)
        return Response({'detail': 'Vente enregistrée avec succès.'})
    except Exception as e:
        return Response({'detail': str(e)}, status=400)

@api_view(['POST'])
def enregistrer_ligne_vente(request, store_id):
    product_id = request.data.get('product_id')
    quantite = request.data.get('quantite', 1)
    if not product_id:
        return Response({'detail': 'Missing product_id.'}, status=400)
    caisse = Caisse(store_id)
    try:
        ligne_vente = caisse.enregistrer_ligne_vente(product_id, quantite)
        return Response({'detail': 'Ligne de vente enregistrée.', 'ligne_vente': {'product_id': ligne_vente.product, 'quantite': ligne_vente.quantite, 'prix': ligne_vente.prix}})
    except Exception as e:
        return Response({'detail': str(e)}, status=400)

@api_view(['POST'])
def update_stock(request, store_id):
    product_id = request.data.get('product_id')
    quantite = request.data.get('quantite', 1)
    if not product_id:
        return Response({'detail': 'Missing product_id.'}, status=400)
    caisse = Caisse(store_id)
    try:
        caisse.update_stock(product_id, quantite)
        return Response({'detail': 'Stock mis à jour avec succès.'})
    except Exception as e:
        return Response({'detail': str(e)}, status=400)
