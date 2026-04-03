"""Management command to send appointment reminders."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking
from services.email_client import send_appointment_reminder
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to send appointment reminders."""
    
    help = 'Send appointment reminders via email (24h before and 1h before)'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            choices=['24h', '1h', 'all'],
            help='Type of reminder to send: 24h, 1h, or all',
        )
    
    def handle(self, *args, **options):
        """Handle command execution."""
        reminder_type = options['type']
        now = timezone.now()
        
        try:
            # Send 24-hour reminders
            if reminder_type in ['24h', 'all']:
                self.send_24h_reminders(now)
            
            # Send 1-hour reminders
            if reminder_type in ['1h', 'all']:
                self.send_1h_reminders(now)
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Appointment reminders sent successfully')
            )
        
        except Exception as e:
            logger.error(f"Error sending reminders: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'✗ Error sending reminders: {str(e)}')
            )
    
    def send_24h_reminders(self, now):
        """Send 24-hour before appointment reminders."""
        # Get bookings that are 24 hours away
        tomorrow_start = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        tomorrow_end = tomorrow_start + timedelta(days=1)
        
        # Find bookings for tomorrow that haven't been reminded
        tomorrow_bookings = Booking.objects.filter(
            slot__date__gte=tomorrow_start.date(),
            slot__date__lt=tomorrow_end.date(),
            reminder_sent_24h=False
        )
        
        sent_count = 0
        for booking in tomorrow_bookings:
            if send_appointment_reminder(booking, hours_before=24):
                booking.reminder_sent_24h = True
                booking.save()
                sent_count += 1
                self.stdout.write(
                    f'  ✓ 24h reminder sent for booking {booking.id}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'  Sent {sent_count} 24-hour reminders')
        )
    
    def send_1h_reminders(self, now):
        """Send 1-hour before appointment reminders."""
        # Get bookings that are happening within the next hour
        one_hour_later = now + timedelta(hours=1)
        
        # Find bookings within next hour that haven't been reminded
        upcoming_bookings = Booking.objects.filter(
            slot__date=now.date(),
            slot__start_time__lte=one_hour_later.time(),
            slot__start_time__gt=now.time(),
            reminder_sent_1h=False
        )
        
        sent_count = 0
        for booking in upcoming_bookings:
            if send_appointment_reminder(booking, hours_before=1):
                booking.reminder_sent_1h = True
                booking.save()
                sent_count += 1
                self.stdout.write(
                    f'  ✓ 1h reminder sent for booking {booking.id}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'  Sent {sent_count} 1-hour reminders')
        )
