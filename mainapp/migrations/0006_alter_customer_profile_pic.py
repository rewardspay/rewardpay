# Generated by Django 3.2.7 on 2021-10-27 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_customer_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
