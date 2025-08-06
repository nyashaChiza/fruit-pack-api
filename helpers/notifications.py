import httpx
import loguru


async def send_push_notification(push_token: str, title: str, body: str):
    message = {
        "to": push_token,
        "sound": "default",
        "title": title,
        "body": body,
        "data": {"extra": "data"},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://exp.host/--/api/v2/push/send", json=message)
        loguru.logger.info(f"Expo response: {response.json()}")