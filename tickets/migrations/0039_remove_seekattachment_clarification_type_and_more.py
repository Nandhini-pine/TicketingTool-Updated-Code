# Generated by Django 5.0.6 on 2024-09-30 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0038_remove_seekattachment_attachment_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seekattachment',
            name='clarification_type',
        ),
        migrations.RemoveField(
            model_name='seekattachment',
            name='file',
        ),
        migrations.RemoveField(
            model_name='seekclarificationhistory',
            name='status',
        ),
        migrations.AddField(
            model_name='seekattachment',
            name='clarification_image',
            field=models.FileField(blank=True, null=True, upload_to='media/clarification_uploads/'),
        ),
        migrations.AddField(
            model_name='seekattachment',
            name='clarified_image',
            field=models.FileField(blank=True, null=True, upload_to='media/clarified_uploads/'),
        ),
        migrations.AlterField(
            model_name='seekclarificationhistory',
            name='seek_comment',
            field=models.TextField(blank=True, help_text='Seek clarification comment.', null=True),
        ),
    ]
