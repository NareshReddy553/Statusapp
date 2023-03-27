from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
import logging 
logger = logging.getLogger("common.mailer")

def send_email(template, context_data, subject, recipient_list, attachments=[]):
    # if settings.DEBUG or getattr(settings, 'SUPRESS_EMAIL', None):
    #     subject = "TEST: %s" % subject
    #     recipient_list = settings.DEBUG_EMAIL_RECIPIENTS
    template = get_template(template)
    context = context_data
    content = template.render(context)
    msg = EmailMessage(
        subject, content, from_email=settings.DEFAULT_FROM_EMAIL, to=recipient_list
    )
    for attachment in attachments:
        msg.attach_file(attachment, mimetype="application/octet-stream")
    msg.content_subtype = "html"
    try:
        msg.send()
        logger.info("-------mail send successfully---------")

    except Exception as e:
        print(e)
        pass
