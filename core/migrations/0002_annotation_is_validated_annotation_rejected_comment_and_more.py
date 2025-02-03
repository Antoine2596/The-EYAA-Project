# Generated by Django 5.1.5 on 2025-01-28 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='is_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='annotation',
            name='rejected_comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='annotation',
            name='validation_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
