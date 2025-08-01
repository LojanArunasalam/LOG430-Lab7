from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
import os 

DATABASE_URL = os.getenv('DATABASE_URL')

class ProductAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1/products/'

    def test_get_all_products(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_product_by_id(self):
        # Assuming a product with ID 1 exists
        response = self.client.get(f'{self.url}1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class StockAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1/stocks/'

    def test_get_all_stocks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_stock_by_id(self):
        # Assuming a stock with ID 1 exists
        response = self.client.get(f'{self.url}1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SalesAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1/sales/'

    def test_get_all_sales(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_sale_by_id(self):
        # Assuming a sale with ID 1 exists
        response = self.client.get(f'{self.url}1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)