# Generated by Django 5.0.6 on 2024-10-01 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0039_remove_seekattachment_clarification_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='seekclarificationhistory',
            name='status_check',
            field=models.CharField(choices=[('clarified', 'clarified'), ('unclarified', 'unclarified')], default='unclarified', max_length=20),
        ),
    ]
