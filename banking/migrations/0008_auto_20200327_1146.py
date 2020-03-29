# Generated by Django 3.0.3 on 2020-03-27 03:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0007_auto_20200327_1034'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='unconfirmedPayments',
            new_name='ApiPayments',
        ),
        migrations.CreateModel(
            name='cancelledPayments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateCancelled', models.DateTimeField(auto_now_add=True, verbose_name='DATE')),
                ('Payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_payment', to='banking.ApiPayments')),
            ],
        ),
    ]