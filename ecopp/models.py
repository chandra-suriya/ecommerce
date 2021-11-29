from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    brandname = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class Wallet(models.Model):
    walletuser = models.OneToOneField(User, on_delete=models.CASCADE)
    walletcount = models.IntegerField(default=0)

    def __str__(self):
        return self.walletuser.username


class Cart(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.owner.username


class Order(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    purchasedate = models.DateField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    brand = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.owner.username


class WalletHistory(models.Model):
    wallets = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    transactiondate = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.wallets.walletuser.username
