# Generated by Django 4.2.4 on 2023-10-10 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_alter_item_approval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvalmatrix',
            name='approval',
            field=models.CharField(choices=[('auto', 'Auto'), ('manual', 'Manual')], max_length=6),
        ),
    ]
