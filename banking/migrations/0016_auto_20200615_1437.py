# Generated by Django 3.0.4 on 2020-06-15 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0015_logs_accountnumber'),
    ]

    operations = [
        migrations.RenameField(
            model_name='logs',
            old_name='accountNumber',
            new_name='receiver',
        ),
        migrations.AddField(
            model_name='logs',
            name='sender',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
