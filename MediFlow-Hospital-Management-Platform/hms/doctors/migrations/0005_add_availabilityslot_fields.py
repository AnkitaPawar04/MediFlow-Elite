"""Migration to add missing columns to doctors_availabilityslot table."""
from django.db import migrations, models, connection


def add_columns(apps, schema_editor):
    """Add missing columns to doctors_availabilityslot table using raw SQL."""
    with connection.cursor() as cursor:
        # Get existing columns
        cursor.execute("PRAGMA table_info(doctors_availabilityslot)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Add is_recurring if it doesn't exist
        if 'is_recurring' not in columns:
            cursor.execute('ALTER TABLE doctors_availabilityslot ADD COLUMN is_recurring INTEGER DEFAULT 0')
        
        # Add max_patients_per_day if it doesn't exist
        if 'max_patients_per_day' not in columns:
            cursor.execute('ALTER TABLE doctors_availabilityslot ADD COLUMN max_patients_per_day INTEGER DEFAULT 10')


def reverse_add_columns(apps, schema_editor):
    """Reverse migration - SQLite doesn't support dropping columns easily."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0004_add_consultation_note_fields'),
    ]

    operations = [
        migrations.RunPython(add_columns, reverse_add_columns),
    ]
