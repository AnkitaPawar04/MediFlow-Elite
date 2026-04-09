import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_email(event, context):
    """
    Entry point for email Lambda.
    """
    try:
        body = json.loads(event.get("body", "{}"))
        action = body.get("action")

        if action == "SIGNUP_WELCOME":
            return signup_welcome(body)

        elif action == "PASSWORD_RESET_OTP":
            return password_reset_otp(body)

        elif action == "BOOKING_CONFIRMATION":
            return booking_confirmation(body)

        elif action == "BOOKING_CONFIRMATION_DOCTOR":
            return booking_confirmation_doctor(body)

        elif action == "BOOKING_CANCELLED":
            return booking_cancelled(body)

        elif action == "APPOINTMENT_REMINDER":
            return appointment_reminder(body)

        return error_response(400, f"Unknown action: {action}")

    except Exception as e:
        logger.error(f"Email service error: {str(e)}")
        return error_response(500, str(e))


# -----------------------
# REQUIRED EMAIL ACTIONS
# -----------------------

def signup_welcome(data):
    validate_required_fields(data, ["recipient_email", "recipient_name", "role"])

    logger.info(
        f"[SIGNUP_WELCOME] Email sent to {data['recipient_email']} "
        f"for role {data['role']}"
    )

    return success_response({
        "message": "Welcome email sent",
        "recipient": data["recipient_email"]
    })


def password_reset_otp(data):
    validate_required_fields(data, ["recipient_email", "recipient_name", "otp"])

    logger.info(
        f"[PASSWORD_RESET_OTP] OTP sent to {data['recipient_email']}"
    )

    return success_response({
        "message": "Password reset OTP email sent",
        "recipient": data["recipient_email"]
    })


def booking_confirmation(data):
    validate_required_fields(
        data,
        ["recipient_email", "recipient_name", "doctor_name", "date", "time"]
    )

    logger.info(
        f"[BOOKING_CONFIRMATION] Email sent to {data['recipient_email']} "
        f"for appointment with {data['doctor_name']} "
        f"on {data['date']} at {data['time']}"
    )

    return success_response({
        "message": "Booking confirmation email sent",
        "recipient": data["recipient_email"]
    })


# -----------------------
# OPTIONAL EMAIL ACTIONS
# -----------------------

def booking_confirmation_doctor(data):
    validate_required_fields(
        data,
        ["recipient_email", "recipient_name", "patient_name", "date", "time"]
    )

    logger.info(
        f"[BOOKING_CONFIRMATION_DOCTOR] Email sent to doctor "
        f"{data['recipient_email']} for patient {data['patient_name']}"
    )

    return success_response({
        "message": "Booking notification sent to doctor",
        "recipient": data["recipient_email"]
    })


def booking_cancelled(data):
    validate_required_fields(
        data,
        ["recipient_email", "recipient_name", "doctor_name", "date", "time"]
    )

    logger.info(
        f"[BOOKING_CANCELLED] Email sent to {data['recipient_email']} "
        f"for cancelled appointment with {data['doctor_name']}"
    )

    return success_response({
        "message": "Cancellation email sent",
        "recipient": data["recipient_email"]
    })


def appointment_reminder(data):
    validate_required_fields(
        data,
        ["recipient_email", "recipient_name", "doctor_name", "date", "time", "hours_before"]
    )

    logger.info(
        f"[APPOINTMENT_REMINDER] Email sent to {data['recipient_email']} "
        f"for appointment with {data['doctor_name']} in {data['hours_before']} hours"
    )

    return success_response({
        "message": "Appointment reminder email sent",
        "recipient": data["recipient_email"]
    })


# -----------------------
# HELPERS
# -----------------------

def validate_required_fields(data, fields):
    missing = [f for f in fields if not data.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def success_response(data):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data),
    }


def error_response(status_code, message):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }
