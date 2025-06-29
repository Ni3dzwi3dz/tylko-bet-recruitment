from rest_framework import serializers

from shop_system.models import Order, Logistic, Product

class AddAddressToOrderRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True, max_length=255)
    products = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1, # Ensure at least one product ID is provided
)


class LogisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logistic
        fields = ['id', 'address', 'delivery_date', 'serialized_products']
        read_only_fields = ['id']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price']
        read_only_fields = ['id'] 
