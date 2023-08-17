from __future__ import absolute_import,unicode_literals

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from django.template.loader import get_template
from django.core.mail import EmailMessage, get_connection

@shared_task
def send_sms_notifications(subject,sms_send_list=[]):
    try:
        send_mail(
            subject="",
            message=subject,
            from_email="status@data-axle.com",  # Replace with your email address
            recipient_list=sms_send_list+['naresh.gangireddy@data-axle.com'],
            fail_silently=False,
        ) 
    except Exception as e:
        print (e)
    return {"status":200}

@shared_task()
def send_email_notifications(template,notifiers,auth_user=None,auth_password=None,fail_silently=False,connection=None):
    try:
        mass_email_obj=[]
        template = get_template(template)
        if notifiers:
            for item in notifiers:
                subject=item['subject']
                context=item['context']
                content = template.render(context)
                recipient_list=item['recipients']
                msg = EmailMessage(
                    subject, content, from_email=settings.DEFAULT_FROM_EMAIL, to=recipient_list
                )
                msg.content_subtype = "html"
                mass_email_obj.append(msg)
        
        connection = connection or get_connection(
            username=auth_user,
            password=auth_password,
            fail_silently=fail_silently,
        )   
        connection.send_messages(mass_email_obj) 
    except Exception as e:
        print (e)
    return {"status":200}