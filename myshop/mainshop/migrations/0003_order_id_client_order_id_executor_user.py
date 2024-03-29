# Generated by Django 5.0.1 on 2024-03-11 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainshop', '0002_order_status_orders'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='id_client',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='id_executor',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(unique=True)),
                ('name', models.CharField(max_length=100)),
                ('orders', models.ManyToManyField(related_name='users', to='mainshop.order')),
            ],
        ),
    ]
