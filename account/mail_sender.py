from email import message
from django.core.mail import send_mail
from django.conf import settings
from random import randint


def send_message(subject, message, send_to):
    return send_mail(subject, message, settings.EMAIL_HOST_USER, [send_to])


def send_code(send_to):
    code = str(randint(111111, 999999))
    subject = 'HSTU OTP CODE'
    message = "This is your hstu code - " + code
    send_message(subject, message, send_to)
    return code
