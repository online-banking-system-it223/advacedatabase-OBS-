# Generated by Django 3.0.3 on 2020-03-26 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0005_auto_20200326_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unconfirmedpayments',
            name='dateConfirmed',
            field=models.DateTimeField(null=True, verbose_name='DATE'),
        ),
    ]
