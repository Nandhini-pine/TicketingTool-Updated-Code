# Generated by Django 4.2.4 on 2023-10-13 04:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0012_item_status_changed_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9\\s]*$', 'Only letters, numbers, and spaces are allowed in the description.')]),
        ),
    ]
