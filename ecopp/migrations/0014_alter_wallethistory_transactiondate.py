# Generated by Django 3.2.9 on 2021-11-19 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecopp', '0013_auto_20211119_0912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallethistory',
            name='transactiondate',
            field=models.DateField(auto_now_add=True),
        ),
    ]
