from celery import shared_task
from django.core.mail import send_mail as django_send_mail


@shared_task
def send_mail_to_admin(text):
    django_send_mail("Reminder", text, 'admin@example.com', ['admin@example.com'])


@shared_task
def notification_to_user(message, user_email):
    django_send_mail("New comment to your post!", message, 'admin@example.com', [user_email])


@shared_task
def contact_us(subject, message, from_email):
    django_send_mail(subject, message, from_email, ['admin@example.com'])
