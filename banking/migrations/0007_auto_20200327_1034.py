# Generated by Django 3.0.3 on 2020-03-27 02:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0006_auto_20200326_2038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unconfirmedpayments',
            old_name='Charge',
            new_name='invoiceId',
        ),
    ]
