"""
Django email backend for development/testing.
Logs emails to console instead of actually sending them.
"""
import logging
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class ConsoleEmailBackend(BaseEmailBackend):
    """
    Email backend that logs emails to console.
    Useful for development and testing without email service.
    """
    
    def send_messages(self, email_messages):
        for message in email_messages:
            logger.info(f"Email sent to {message.to}: {message.subject}")
        return len(email_messages)
