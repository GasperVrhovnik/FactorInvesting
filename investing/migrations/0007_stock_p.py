# Generated by Django 3.0 on 2020-01-26 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0006_auto_20200125_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='p',
            field=models.BooleanField(default=False, verbose_name='p'),
        ),
    ]
