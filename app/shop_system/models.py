from django.db import models
from simple_history.models import HistoricalRecords


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=16)
    history = HistoricalRecords()


class Order(models.Model):
    address = models.CharField(max_length=255)
    placed_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product, related_name="orders")
    history = HistoricalRecords()


class Logistic(models.Model):
    order = models.ForeignKey(Order, related_name="logistics", on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    delivery_date = models.DateTimeField(null=True, blank=True)
    serialized_products = models.JSONField(default=list)
    history = HistoricalRecords()