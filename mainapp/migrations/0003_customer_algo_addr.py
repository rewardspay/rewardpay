# Generated by Django 3.2.7 on 2021-10-27 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='algo_addr',
            field=models.CharField(max_length=500, null=True),
        ),
    ]