# Generated by Django 3.2.7 on 2021-10-27 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_customer_algo_addr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='algo_addr',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
