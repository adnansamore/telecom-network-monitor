import os
import requests


def notify_console(message: str) -> None:
    print(f"[ALERT] {message}")


def notify_slack(message: str):
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return
    try:
        requests.post(url, json={"text": message}, timeout=5)
    except Exception:
        pass


def send_alert(msg: str):
    notify_console(msg)
    notify_slack(msg)