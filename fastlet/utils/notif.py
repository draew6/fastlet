from ..models.notif import MassNotificationBody, MassNotificationResponse
from pywebpush import webpush, WebPushException
from .settings import NotifSettings


async def send_notifications(
    body: MassNotificationBody, settings: NotifSettings
) -> MassNotificationResponse:
    notified_devices = []
    failed_to_notify_devices = []

    for device in body.devices:
        try:
            webpush(
                subscription_info=device.subscription_info,
                data=body.message,
                vapid_private_key=settings.vapid_key,
                vapid_claims={"sub": f"mailto:{settings.vapid_mailto}"},
            )
            notified_devices.append(device)
        except WebPushException:
            failed_to_notify_devices.append(device)

    return MassNotificationResponse(
        success=notified_devices, failed=failed_to_notify_devices
    )
