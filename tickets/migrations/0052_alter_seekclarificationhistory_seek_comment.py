# Generated by Django 5.0.6 on 2024-10-08 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0051_alter_subcategory_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seekclarificationhistory',
            name='seek_comment',
            field=models.TextField(default=1, help_text='Seek clarification comment.'),
            preserve_default=False,
        ),
    ]