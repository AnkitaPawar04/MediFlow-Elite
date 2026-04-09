# Generated migration for Booking model updates - Payment fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_booking_reminder_sent_1h_booking_reminder_sent_24h'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Add new patient field as ForeignKey (nullable initially)
        migrations.AddField(
            model_name='booking',
            name='patient_fk',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='accounts.customuser'),
        ),
        
        # Copy data from old patient field to new field
        migrations.RunSQL(
            "UPDATE bookings_booking SET patient_fk_id = patient_id WHERE patient_id IS NOT NULL;",
            reverse_sql="",
        ),
        
        # Remove old patient field
        migrations.RemoveField(
            model_name='booking',
            name='patient',
        ),
        
        # Rename new field to patient
        migrations.RenameField(
            model_name='booking',
            old_name='patient_fk',
            new_name='patient',
        ),
        
        # Alter patient field to NOT NULL with constraints
        migrations.AlterField(
            model_name='booking',
            name='patient',
            field=models.ForeignKey(limit_choices_to={'role': 'PATIENT'}, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='accounts.customuser'),
        ),
        
        # Add new fields
        migrations.AddField(
            model_name='booking',
            name='consultation_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', help_text='Payment status for the consultation', max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_id',
            field=models.CharField(blank=True, help_text='Razorpay payment ID', max_length=100, null=True),
        ),
    ]
