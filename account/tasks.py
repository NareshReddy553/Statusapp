from __future__ import absolute_import,unicode_literals

from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_sms_notifications(subject,sms_subscribers=[]):
    try:
        send_mail(
            subject="",
            message=subject,
            from_email="status@data-axle.com",  # Replace with your email address
            recipient_list=sms_subscribers,
            fail_silently=False,
        ) 
    except Exception as e:
        print (e)
    return True

            