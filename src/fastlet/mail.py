import resend
from pydantic_settings import BaseSettings, SettingsConfigDict


class MailSettings(BaseSettings):
    resend_api_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


async def send_mail(address_from: str, addresses_to: list[str], subject: str, html_content: str):
    settings = MailSettings()
    resend.api_key = settings.resend_api_key

    mail_params: resend.Emails.SendParams = {
        "from": address_from,
        "to": addresses_to,
        "subject": subject,
        "html": html_content
    }
    await resend.Emails.send_async(mail_params)