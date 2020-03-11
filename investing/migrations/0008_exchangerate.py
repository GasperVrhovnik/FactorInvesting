# Generated by Django 3.0 on 2020-02-02 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0007_stock_p'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=10, unique=True)),
                ('date', models.DateTimeField(verbose_name='date')),
                ('rate', models.DecimalField(decimal_places=6, default=0, max_digits=12, verbose_name='Rate')),
            ],
        ),
    ]
