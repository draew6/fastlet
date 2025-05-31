import sendgrid
from .settings import get_settings
from sendgrid.helpers.mail import Mail, Email, To, HtmlContent


def send_mail(to: str, subject: str, content: str):
    settings = get_settings("auth")
    sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
    from_email = Email(settings.sendgrid_from_mail)
    to_email = To(to)
    content = HtmlContent(content)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    if response.status_code != 202:
        raise Exception("Sendgrid error")


def get_mail_sender():
    return send_mail


def get_mail_sender_mock():
    return lambda x: None
