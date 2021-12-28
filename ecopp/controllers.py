from ecopp import models
from rest_framework import serializers


class ProductControllers:
    def addproducts(self, name: str, category_id: int, price: int,
                    brandname: str,
                    description: str, quantity: int):
        if(models.Category.objects.filter(id=category_id).exists()):
            categ = models.Category.objects.get(id=category_id)
            pro = models.Product.objects.create(name=name, category=categ,
                                                price=price,
                                                brandname=brandname,
                                                description=description,
                                                quantity=quantity)
        else:
            raise serializers.ValidationError(
                {"result": False, "msg": "category is not included"},
                code="validation_error",
                )
        return pro.id

    def viewproducts(self):
        prolist = models.Product.objects.filter(quantity__gte=1)  # __gte is
        if not (prolist):
            raise serializers.ValidationError(
                {"result": False, "msg": "products are empty"},
                code="validation_error",
            )
        return prolist

    def list_pro_category(self, pk: int):
        cate = models.Category.objects.get(name=pk)
        data = models.Product.objects.filter(category=cate)
        return data


class CartControllers:

    def add_cart(self, user: object, product: str, quantites: int):
        pro = models.Product.objects.get(name=product)
        if(int(quantites) > pro.quantity):
            raise serializers.ValidationError(
                {"result": False, "msg": "stocks quantity is more"},
                code="validation_error",
            )
        if(models.Cart.objects.filter(owner=user, product=pro).exists()):
            cart = models.Cart.objects.get(owner=user, product=pro)
            cart.quantity = cart.quantity + int(quantites)
            cart.save()
        else:
            cart = models.Cart.objects.create(owner=user, product=pro,
                                              quantity=quantites)
        pro.quantity = pro.quantity - int(quantites)
        pro.save()
        data = {
                "id":  pro.id,
                "name": user.username,
                "product": pro.name,
                "quantity": cart.quantity,
              }
        return data
