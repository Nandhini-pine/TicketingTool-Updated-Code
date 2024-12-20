# Generated by Django 5.0.6 on 2024-09-27 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0025_alter_item_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='seek_clarification_attachments',
            field=models.FileField(blank=True, help_text='Attachments for the clarification request.', upload_to='attachments/'),
        ),
        migrations.AddField(
            model_name='item',
            name='seek_clarification_cmnt',
            field=models.TextField(blank=True, help_text='Comments regarding the clarification request.'),
        ),
    ]
