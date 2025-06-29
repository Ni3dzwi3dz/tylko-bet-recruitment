from django.views import View

from shop_system.services import AddAddressToOrderService
from shop_system.serializers import AddAddressToOrderRequestSerializer


import json
from django.http import JsonResponse
from shop_system.models import Order, Product, Logistic
from shop_system.exceptions import OrderNotFoundError, ProductNotFoundError, ProductNotInOrderError


class AddAddressToOrderView(View):
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        serializer = AddAddressToOrderRequestSerializer(data=data)

        if not serializer.is_valid():
            return JsonResponse({"error": "Missing required fields",
                                 "details": serializer.errors},
                                   status=400)

        order_id = serializer.validated_data["order_id"]
        new_address = serializer.validated_data["address"]
        products = serializer.validated_data["products"]

        try:
            order = AddAddressToOrderService.get_order_if_exists(order_id)

            AddAddressToOrderService.validate_requested_products(products=products, order_id=order.id)

            new_products = AddAddressToOrderService.extract_products_from_existing_logistics(products, order_id=order.id)

            new_logistic = Logistic.objects.create(
                order=order,
                address=new_address,
                delivery_date=None,
                serialized_products=new_products
            )

            return JsonResponse({
                "message": "Order address added successfully",
                "logistic": {
                    "logistic_id": new_logistic.id,
                    "address": new_logistic.address,
                    "delivery_date": new_logistic.delivery_date,
                    "products": new_logistic.serialized_products
                }
            }, status=200)
        
        except OrderNotFoundError as e:
            return JsonResponse({"error": str(e)}, status=404)

        except ProductNotFoundError as e:
            return JsonResponse({"error": str(e)}, status=400)
        
        except ProductNotInOrderError as e:
            return JsonResponse({"error": str(e)}, status=400)