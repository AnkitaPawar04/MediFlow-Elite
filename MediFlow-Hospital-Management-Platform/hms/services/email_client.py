import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_signup_welcome(user):
    payload = {
        'action': 'SIGNUP_WELCOME',
        'recipient_email': user.email,
        'recipient_name': user.get_full_name(),
        'role': user.get_role_display(),
    }

    try:
        requests.post(
            f"{settings.EMAIL_SERVICE_URL}/send-email",
            json=payload,
            timeout=5
        )
    except Exception as e:
        logger.error(f"Welcome email failed: {e}")


def send_booking_confirmation(booking):
    try:
        # Patient
        requests.post(
            f"{settings.EMAIL_SERVICE_URL}/send-email",
            json={
                'action': 'BOOKING_CONFIRMATION',
                'recipient_email': booking.patient.email,
                'recipient_name': booking.patient.get_full_name(),
                'doctor_name': booking.doctor.get_full_name(),
                'date': str(booking.slot.date),
                'time': str(booking.slot.start_time),
            },
            timeout=5
        )

        # Doctor (optional)
        requests.post(
            f"{settings.EMAIL_SERVICE_URL}/send-email",
            json={
                'action': 'BOOKING_CONFIRMATION_DOCTOR',
                'recipient_email': booking.doctor.email,
                'recipient_name': booking.doctor.get_full_name(),
                'patient_name': booking.patient.get_full_name(),
                'date': str(booking.slot.date),
                'time': str(booking.slot.start_time),
            },
            timeout=5
        )

    except Exception as e:
        logger.error(f"Booking email failed: {e}")


def send_booking_cancelled(booking):
    payload = {
        'action': 'BOOKING_CANCELLED',
        'recipient_email': booking.patient.email,
        'recipient_name': booking.patient.get_full_name(),
        'doctor_name': booking.doctor.get_full_name(),
        'date': str(booking.slot.date),
        'time': str(booking.slot.start_time),
    }

    try:
        requests.post(
            f"{settings.EMAIL_SERVICE_URL}/send-email",
            json=payload,
            timeout=5
        )
    except Exception as e:
        logger.error(f"Cancellation email failed: {e}")


def send_appointment_reminder(booking, hours_before=1):
    payload = {
        'action': 'APPOINTMENT_REMINDER',
        'recipient_email': booking.patient.email,
        'recipient_name': booking.patient.get_full_name(),
        'doctor_name': booking.doctor.get_full_name(),
        'date': str(booking.slot.date),
        'time': str(booking.slot.start_time),
        'hours_before': hours_before,
    }

    try:
        requests.post(
            f"{settings.EMAIL_SERVICE_URL}/send-email",
            json=payload,
            timeout=5
        )
        return True
    except Exception as e:
        logger.error(f"Reminder email failed: {e}")
        return False
