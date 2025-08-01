from ..repositories.product_repository import ProductRepository
import logging 
import requests

class ProductService: 
    def __init__(self, session):
        self.session = session
        # Garder le repository comme fallback si nécessaire
        self.product_repository = ProductRepository(session)
        
        # Configuration du microservice products
        self.products_service_url = "http://localhost:8000/products"

    def get_product_by_id(self, id):
        """Récupérer un produit depuis le microservice products"""
        try:
            response = requests.get(f"{self.products_service_url}/api/v1/products/{id}")
            if response.status_code == 200:
                print("something")
                return response.json()
            elif response.status_code == 404:
                logging.warning(f"Produit {id} non trouvé dans le microservice")
                return None
            else:
                logging.error(f"Erreur microservice products: {response.status_code}")
                # Fallback vers repository local si microservice échoue
                return self.product_repository.get_by_id(id)
        except Exception as e:
            logging.error(f"Erreur connexion microservice products: {e}")
            # Fallback vers repository local
            return self.product_repository.get_by_id(id)
    
    def get_all_products(self):
        """Récupérer tous les produits depuis le microservice products"""
        try:
            response = requests.get(f"{self.products_service_url}/api/v1/products")
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Erreur microservice products: {response.status_code}")
                # Fallback vers repository local
                return self.product_repository.get_all_products()
        except Exception as e:
            logging.error(f"Erreur connexion microservice products: {e}")
            # Fallback vers repository local
            return self.product_repository.get_all_products()

    def get_product_by_category(self, category):
        """Récupérer produits par catégorie depuis le microservice products"""
        try:
            response = requests.get(f"{self.products_service_url}/api/v1/products/category/{category}")
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Erreur microservice products: {response.status_code}")
                # Fallback vers repository local
                return self.product_repository.get_product_by_category(category)
        except Exception as e:
            logging.error(f"Erreur connexion microservice products: {e}")
            # Fallback vers repository local
            return self.product_repository.get_product_by_category(category)

    def add_product(self, product_data):
        """Ajouter un produit via le microservice products"""
        try:
            # Convertir l'objet product en dictionnaire si nécessaire
            if hasattr(product_data, '__dict__'):
                payload = {
                    'name': product_data.name,
                    'category': product_data.category,
                    'description': product_data.description,
                    'prix_unitaire': product_data.prix_unitaire
                }
            else:
                payload = product_data
            
            response = requests.post(
                f"{self.products_service_url}/api/v1/products",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Erreur ajout produit microservice: {response.status_code}")
                # Fallback vers repository local
                return self.product_repository.add_product(product_data)
        except Exception as e:
            logging.error(f"Erreur connexion microservice products: {e}")
            # Fallback vers repository local
            return self.product_repository.add_product(product_data)
    
    def update_product(self, product_id, product_data):
        """Mettre à jour un produit via le microservice products"""
        try:
            # Convertir l'objet product en dictionnaire si nécessaire
            if hasattr(product_data, '__dict__'):
                payload = {
                    'name': product_data.name,
                    'category': product_data.category,
                    'description': product_data.description,
                    'prix_unitaire': product_data.prix_unitaire
                }
            else:
                payload = product_data
            
            response = requests.put(
                f"{self.products_service_url}/api/v1/products/{product_id}",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Erreur mise à jour produit microservice: {response.status_code}")
                # Fallback vers repository local
                return self.product_repository.update_product(product_data)
        except Exception as e:
            logging.error(f"Erreur connexion microservice products: {e}")
            # Fallback vers repository local
            return self.product_repository.update_product(product_data)
    
    def delete_product(self, product_id):
        """Supprimer un produit via le microservice products"""
        try:
            response = requests.delete(f"{self.products_service_url}/api/v1/products/{product_id}")
            
            if response.status_code == 200:
                return {"detail": "Product deleted successfully"}
            else:
                logging.error(f"Erreur suppression produit microservice: {response.status_code}")
                # Fallback vers repository local
                return self.product_repository.delete_product(product_id)
        except Exception as e:
            logging.error(f"Erreur connexion microservice products: {e}")
            # Fallback vers repository local
            return self.product_repository.delete_product(product_id)

    def validate_product_exists(self, product_id):
        """Valider qu'un produit existe - utile pour la caisse"""
        try:
            response = requests.get(f"{self.products_service_url}/api/v1/products/{product_id}/exists")
            if response.status_code == 200:
                data = response.json()
                return data.get("exists", False)
            return False
        except Exception as e:
            logging.error(f"Erreur validation produit: {e}")
            # Fallback : vérifier localement
            product = self.product_repository.get_by_id(product_id)
            return product is not None

    def get_product_price(self, product_id):
        """Récupérer le prix d'un produit - utile pour la caisse"""
        product = self.get_product_by_id(product_id)
        if product:
            return product.get('prix_unitaire') if isinstance(product, dict) else product.prix_unitaire
        return None