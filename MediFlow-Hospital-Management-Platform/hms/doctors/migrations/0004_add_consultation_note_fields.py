# Migration to add missing columns to doctors_consultation_note table
from django.db import migrations, models
from django.db import connection


def add_columns(apps, schema_editor):
    """Add missing columns to doctors_consultation_note table using raw SQL."""
    with connection.cursor() as cursor:
        # Get existing columns
        cursor.execute("PRAGMA table_info(doctors_consultation_note)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Add followup_required if it doesn't exist
        if 'followup_required' not in columns:
            cursor.execute('ALTER TABLE doctors_consultation_note ADD COLUMN followup_required INTEGER DEFAULT 0')
        
        # Add followup_date if it doesn't exist
        if 'followup_date' not in columns:
            cursor.execute('ALTER TABLE doctors_consultation_note ADD COLUMN followup_date DATE')


def reverse_add_columns(apps, schema_editor):
    """Reverse migration - SQLite doesn't support dropping columns easily."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0003_add_missing_models'),
    ]

    operations = [
        migrations.RunPython(add_columns, reverse_add_columns),
    ]
