# Generated by Django 3.0.3 on 2020-03-24 08:59

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0002_delete_bankcryptographykeys'),
    ]

    operations = [
        migrations.CreateModel(
            name='apiTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction', django.contrib.postgres.fields.jsonb.JSONField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactionOwner', to='banking.account')),
                ('parentTransaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_transaction', to='banking.transaction')),
            ],
        ),
    ]
