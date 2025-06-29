from shop_system.models import Order, Logistic, Product
from shop_system.exceptions import OrderNotFoundError, ProductNotFoundError, ProductNotInOrderError

from typing import Optional

class OrderAddressUpdateService: # TODO think about more meaningful name
    
    @staticmethod
    def get_order_if_exists(order_id) -> Order:
        order = Order.objects.filter(id=order_id).first()
        if not order:
            raise OrderNotFoundError(f"Order with id {order_id} does not exist.")
        return order
    
    @staticmethod
    def validate_requested_products(products, order_id=None) -> None:
        OrderAddressUpdateService.check_if_all_products_exist_in_order(products, order_id)
        
        for product in products:
            OrderAddressUpdateService.check_if_product_exists_in_database(product)    

    @staticmethod
    def check_if_all_products_exist_in_order(products, order_id) -> None:
        order = OrderAddressUpdateService.get_order_if_exists(order_id)
        existing_products = order.products.values_list('id', flat=True)
        
        for product in products:
            if product not in existing_products:
                raise ProductNotInOrderError(f"Product with id {product} does not exist in order {order_id}.")

    @staticmethod
    def check_if_product_exists_in_database(product_id) -> None:
        if not Product.objects.filter(id=product_id).exists():
            raise ProductNotFoundError(f"Product with id {product_id} does not exist in the database.")

    @staticmethod
    def extract_products_from_existing_logistics(products, order_id) -> dict:
        existing_order_logistics = Logistic.objects.filter(order_id=order_id).all()
        
        extracted_products = {}
            
        for logistic in existing_order_logistics:
            for product in products:
                if str(product) in logistic.serialized_products.keys():
                    extracted_products[product] = logistic.serialized_products.pop(str(product))
                    Logistic.objects.filter(id=logistic.id).update(
                        address=logistic.address,
                        delivery_date=logistic.delivery_date,
                        serialized_products=logistic.serialized_products
                    )
        return extracted_products
    
    @staticmethod
    def check_if_logistic_with_given_address_exists(order_id, address) -> Optional[Logistic]:
        existing_logistics = Logistic.objects.filter(order_id=order_id, address=address).first()
        if existing_logistics:
            return existing_logistics
        return None
    
    @staticmethod
    def update_existing_logistic(logistic, products) -> None: 
        for product in products:
            if product.id in logistic.serialized_products:
                logistic.serialized_products.pop(product.id)
        
        Logistic.objects.filter(id=logistic.id).update(
            address=logistic.address,
            delivery_date=logistic.delivery_date,
            serialized_products=logistic.serialized_products
        )
