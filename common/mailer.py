from django.conf import settings
from django.core.mail import EmailMessage,get_connection
from django.template.loader import get_template
import logging 
logger = logging.getLogger("common.mailer")


def send_mass_mail(msg, fail_silently=False, auth_user=None,
                   auth_password=None, connection=None):
    
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )

    return connection.send_messages(msg)


def send_email(template, context_data, subject, recipient_list, attachments=[]):
  
    template = get_template(template)
    context = context_data
    content = template.render(context)
    msg = EmailMessage(subject, content, from_email=settings.DEFAULT_FROM_EMAIL, to=recipient_list)
    for attachment in attachments:
        msg.attach_file(attachment, mimetype="application/octet-stream")
    msg.content_subtype = "html"
    return msg
    

