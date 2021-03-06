# Generated by Django 3.0 on 2020-02-09 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0013_operatingprofitability'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharesOutstanding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=0, verbose_name='year')),
                ('sharesOutstanding', models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='Shares Outstanding')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='investing.Stock')),
            ],
        ),
        migrations.CreateModel(
            name='PriceToBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=0, verbose_name='year')),
                ('PB', models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='P/B')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='investing.Stock')),
            ],
        ),
        migrations.CreateModel(
            name='MarketCapInDollars',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=0, verbose_name='year')),
                ('marketCap', models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='Shares Outstanding')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='investing.Stock')),
            ],
        ),
        migrations.CreateModel(
            name='MarketCap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=0, verbose_name='year')),
                ('marketCap', models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='Shares Outstanding')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='investing.Stock')),
            ],
        ),
    ]
