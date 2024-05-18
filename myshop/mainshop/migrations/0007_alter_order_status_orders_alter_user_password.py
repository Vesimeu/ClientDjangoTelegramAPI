# Generated by Django 5.0.1 on 2024-05-18 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainshop', '0006_user_token_alter_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status_orders',
            field=models.CharField(choices=[('pending', 'В ожидании'), ('in_progress', 'В процессе'), ('completed', 'Завершен')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$P0Vr81nRMu7NAYtXn6GXAR$VPLAUOMmvHbV0QIa2cVcUHvx6su1xshd0QylmizoPlQ=', max_length=128, verbose_name='password'),
        ),
    ]
