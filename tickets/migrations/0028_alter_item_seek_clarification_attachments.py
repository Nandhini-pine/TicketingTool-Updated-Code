# Generated by Django 5.0.6 on 2024-09-27 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0027_alter_item_seek_clarification_attachments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='seek_clarification_attachments',
            field=models.FileField(blank=True, help_text='Attachments for the clarification request.', upload_to='attachments/'),
        ),
    ]
