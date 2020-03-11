# Generated by Django 3.0 on 2020-01-25 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0004_stock_yahoo_ticker'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='currency',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=10, verbose_name='Currency'),
        ),
    ]
