# Generated by Django 4.2.4 on 2023-10-10 09:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_alter_item_approval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='approval',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tickets.approvalmatrix'),
        ),
    ]
