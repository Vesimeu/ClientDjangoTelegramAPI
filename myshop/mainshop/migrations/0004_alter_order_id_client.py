# Generated by Django 5.0.1 on 2024-03-11 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainshop', '0003_order_id_client_order_id_executor_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='id_client',
            field=models.BigIntegerField(default=0),
        ),
    ]
