# Generated by Django 3.0 on 2020-02-10 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0015_investment'),
    ]

    operations = [
        migrations.AddField(
            model_name='holding',
            name='allFactors',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='allFactors'),
        ),
        migrations.AddField(
            model_name='holding',
            name='investment',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='Investment'),
        ),
        migrations.AddField(
            model_name='holding',
            name='profitability',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='Profitability'),
        ),
        migrations.AddField(
            model_name='holding',
            name='value',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='holding',
            name='weight',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='Weight'),
        ),
    ]