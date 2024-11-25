# Generated by Django 5.0.6 on 2024-10-05 05:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0048_rename_created_by_statushistory_changed_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusChangeHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('open', 'Open'), ('assigned', 'Assigned'), ('inprogress', 'In Progress'), ('pending', 'Pending'), ('Resolved', 'Resolved'), ('closed', 'Closed'), ('reopen', 'Re-Open'), ('seek-clarification', 'seek-clarification')], max_length=20)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_changes', to='tickets.item')),
            ],
        ),
        migrations.DeleteModel(
            name='StatusHistory',
        ),
    ]