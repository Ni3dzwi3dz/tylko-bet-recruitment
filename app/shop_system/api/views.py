# class based view insteaad of function based view
def add_order_adress(request):
    data = json.loads(request.body)

    order_id = data.get("order_id") # use serializers 
    products = data.get("products")
    new_address = data.get("address")

    if not order_id or not products or not new_address:
        return JsonResponse({"error": "Missing required fields"}, status=400)
    
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return JsonResponse({"error": "Order not found"}, status=404)
    
    for product in products:
        if not Product.objects.filter(id=product).exists():
            return JsonResponse({"error": f"Product {product} not found"}, status=404)
    
    existing_order_logistics = Logistic.objects.filter(order=order).all()

    new_products = {}

    for logistic in existing_order_logistics:
        for product in products: # use Queryset
            if product.id in logistic.serialized_products.keys():
                new_products[product.id] = logistic.serialized_products.pop(product.id)
                Logistic.objects.filter(id=logistic.id).update(
                    address=logistic.address,
                    delivery_date=logistic.delivery_date,
                    serialized_products=logistic.serialized_products
                )

    new_logistic = Logistic.objects.create(
        order=order,
        address=new_address,
        delivery_date=None,
        serialized_products=new_products
    )

    return JsonResponse({ # again - serializer 
        "message": "Order address added successfully",
        "logistic": 
        {"logistic_id": new_logistic.id,
        "address": new_logistic.address,
        "delivery_date": new_logistic.delivery_date,
        "products": new_logistic.serialized_products}
                }, status=200)



                