from rest_framework import serializers
from ecopp import models


class ProductSerializer(serializers.ModelSerializer):
    categories_data = serializers.SerializerMethodField('get_category_name')
    # no_of_stocks = serializers.SerializerMethodField('get_no_of_stocks')

    class Meta:
        model = models.Product
        fields = ['name', 'categories_data',
                  'price', 'brandname', 'description']

    def get_category_name(self, entry_ind):
        user = entry_ind.category.name  # one to many relationship
        return user


class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField('get_product_name')
    product_amount = serializers.SerializerMethodField('get_product_amount')

    class Meta:
        model = models.Cart
        fields = ['id', 'product_name', 'product_amount', 'quantity']

    def get_product_name(self, prod_ind):
        prod = prod_ind.product.name  # one to many relationship
        return prod

    def get_product_amount(self, prod_ind):
        prod = prod_ind.product.price  # one to many relationship
        return prod


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField('get_product_name')

    class Meta:
        model = models.Order
        fields = ['id', 'product_name', 'price', 'purchasedate']

    def get_product_name(self, prod_ind):
        prod = prod_ind.product.name  # one to many relationship
        return prod


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WalletHistory
        fields = ['amount', 'transactiondate']
