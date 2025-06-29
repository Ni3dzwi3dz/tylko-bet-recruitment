import json

from rest_framework.test import APITestCase
from shop_system.serializers import ProductSerializer
from shop_system.models import Order, Logistic, Product
from datetime import datetime

class AddAddressToOrderTestCase(APITestCase):
    def setUp(self):
        self.new_address = '456 New Address St'
        # Create sample products
        self.products = [
            Product.objects.create(name='Product 1', description='Description 1', price=10.0),
            Product.objects.create(name='Product 2', description='Description 2', price=20.0),
            Product.objects.create(name='Product 3', description='Description 3', price=30.0),
            Product.objects.create(name='Product 4', description='Description 4', price=40.0)
        ]
   
        # Create a sample order
        self.order = Order.objects.create(
        address='123 Sample Address',
        placed_at=datetime.now(),
    )
        self.order.products.set(Product.objects.all()[:3])

        # Create a logistic entry for the order
        self.logistic = Logistic.objects.create(
            order=self.order,
            address='123 Sample Address',
            delivery_date=None,
            serialized_products={
            product['id']: product
            for product in ProductSerializer(Product.objects.all()[:3], many=True).data
        }
    )

    def test_add_address_to_order_with_correct_request(self):
        self.assertEqual(Logistic.objects.count(), 1)
        self.assertEqual(Logistic.history.count(),1) 

        response = self.client.post('/address/', {
            'order_id': self.order.id,
            'address': self.new_address,
            'products': [self.products[0].id, self.products[1].id]
        }, format='json')


        self.assertEqual(response.status_code, 200)
        self.assertIn('logistic', response.json())
        self.assertEqual(response.json()['logistic']['address'], self.new_address)
        self.assertEqual(response.json()['logistic']['products'], {
            str(self.products[0].id): ProductSerializer(self.products[0]).data,
            str(self.products[1].id): ProductSerializer(self.products[1]).data
        })
        self.assertEqual(Logistic.objects.count(), 2)  # One new logistic entry should be created

        self.assertEqual(Logistic.history.count(), 2)  # One new logistic history entry should be created

    def test_add_address_to_order_with_nonexistent_order(self):
        non_existent_order_id = 9999
        self.assertFalse(Order.objects.filter(id=non_existent_order_id).exists())

        response = self.client.post('/address/', {
            'order_id': non_existent_order_id,
            'address': self.new_address,
            'products': [self.products[0].id, self.products[1].id]
        }, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_add_address_to_order_with_nonexistent_product(self):
        non_existent_product_id = 99999
        self.assertFalse(Product.objects.filter(id=non_existent_product_id).exists())

        response = self.client.post('/address/', {
            'order_id': self.order.id,
            'address': self.new_address,
            'products': [non_existent_product_id]
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_add_address_to_order_with_empty_products(self):
        
        response = self.client.post('/address/', {
            'order_id': self.order.id,
            'address': self.new_address,
            'products': []
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_add_address_to_order_with_invalid_request(self):
        response = self.client.post('/address/', {
            'order_id': self.order.id,
            'address': self.new_address,
            'foo': 'bar'  # Invalid field
        }, format='json')
        

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_add_address_to_order_with_products_not_in_order(self):
        response = self.client.post('/address/', {
            'order_id': self.order.id,
            'address': self.new_address,
            'products': [self.products[0].id, self.products[3].id]
        }, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
