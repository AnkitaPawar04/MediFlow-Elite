import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_signup_welcome(user):
    if not settings.EMAIL_SERVICE_URL:
        logger.warning("EMAIL_SERVICE_URL not configured. Skipping welcome email.")
        return
    
    payload = {
        'action': 'SIGNUP_WELCOME',
        'recipient_email': user.email,
        'recipient_name': user.get_full_name(),
        'role': user.get_role_display(),
    }

    try:
        response = requests.post(
            f"{settings.EMAIL_SERVICE_URL}/send-email",
            json=payload,
            timeout=5
        )
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Welcome email failed: {e}")


def send_password_reset_otp(user, otp):
    """Send OTP for password reset."""
    payload = {
        'action': 'PASSWORD_RESET_OTP',
        'recipient_email': user.email,
        'recipient_name': user.get_full_name(),
        'otp': otp,
    }

    if not settings.EMAIL_SERVICE_URL:
        # Development mode: log OTP to console for testing
        logger.warning(f"⚠️  EMAIL_SERVICE_URL not configured!")
        logger.warning(f"📧 Password Reset OTP for {user.email}: {otp}")
        logger.warning(f"ℹ️  To enable email service, set EMAIL_SERVICE_URL in .env file")
        logger.warning(f"ℹ️  Example: EMAIL_SERVICE_URL=http://localhost:3000/dev")
        # Still raise exception as required by caller
        raise Exception("Email service not configured - Development Mode: OTP logged to console")
    
    try:
        response = requests.post(
            f"{settings.EMAIL_SERVICE_URL}/send-email",
            json=payload,
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"Password reset OTP sent to {user.email}")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Could not connect to email service at {settings.EMAIL_SERVICE_URL}")
        logger.error(f"To run email service locally: cd email-service && serverless offline start")
        # FALLBACK: Log OTP to console for development
        logger.warning(f"\n{'='*60}")
        logger.warning(f"📧 DEVELOPMENT MODE - Password Reset OTP")
        logger.warning(f"{'='*60}")
        logger.warning(f"User Email: {user.email}")
        logger.warning(f"OTP Code: {otp}")
        logger.warning(f"{'='*60}\n")
        raise Exception("Email service is unavailable - OTP logged to console for development")
    except Exception as e:
        logger.error(f"Password reset OTP email failed: {e}")
        # FALLBACK: Log OTP to console for development
        logger.warning(f"\n{'='*60}")
        logger.warning(f"📧 DEVELOPMENT MODE - Password Reset OTP")
        logger.warning(f"{'='*60}")
        logger.warning(f"User Email: {user.email}")
        logger.warning(f"OTP Code: {otp}")
        logger.warning(f"{'='*60}\n")
        raise


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
