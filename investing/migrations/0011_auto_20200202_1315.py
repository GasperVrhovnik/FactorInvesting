# Generated by Django 3.0 on 2020-02-02 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0010_auto_20200202_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangerate',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
