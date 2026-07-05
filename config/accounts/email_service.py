import threading
from django.core.mail import send_mail
from django.conf import settings


def send_email_thread(subject, message, recipient_list):
    def send_email():
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {e}")

    email_thread = threading.Thread(target=send_email)
    email_thread.daemon = True
    email_thread.start()