# Generated by Django 3.0 on 2020-02-27 12:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0017_auto_20200227_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cogs',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investing.Stock'),
        ),
    ]
