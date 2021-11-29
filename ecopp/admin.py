from django.contrib import admin
from ecopp import models
# Register your models here.

admin.site.register(models.Category)
admin.site.register(models.Product)
admin.site.register(models.Wallet)
admin.site.register(models.Cart)
admin.site.register(models.Order)
admin.site.register(models.WalletHistory)
