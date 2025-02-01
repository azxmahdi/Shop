from celery import shared_task
from mail_templated import EmailMessage

@shared_task
def send_email(tpl_name, context:dict, email, to:list):
    message = EmailMessage(tpl_name, context, email, to=to)
    message.send()
