from celery import shared_task
from mail_templated import EmailMessage


@shared_task
def send_email_task(template, data, from_email, to):
    email_obj = EmailMessage(
        template,
        data,
        from_email,
        to=to,
    )
    print("pppppp")
    email_obj.send()
