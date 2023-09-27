from typing import Any
import requests
import traceback
from datetime import datetime
from app.AggroConfig import AggroConfigSendGridAlerter
from dataclasses import asdict


class SendGridAlerter:
    @staticmethod
    def from_config(config: AggroConfigSendGridAlerter) -> "SendGridAlerter":
        return SendGridAlerter(**asdict(config))

    def __init__(
        self,
        api_token: str,
        email_from: str,
        email_to: list[str],
    ):
        self.email_from = email_from
        self.email_to = email_to
        self.api_token = api_token

    def send_alert(self, text: str):
        try:
            now = datetime.now()
            now_text = now.strftime("%a, %d %b %Y %H:%M:%S +0000")
            to_lst = [{"email": email} for email in self.email_to]
            subject = f"Aggro alert on {now_text}"
            API_URL = "https://api.sendgrid.com/v3/mail/send"
            data = {
                "personalizations": [{"to": to_lst}],
                "from": {"email": self.email_from},
                "subject": subject,
                "content": [
                    {
                        "type": "text/plain",
                        "value": text,
                    }
                ],
            }
            r = requests.post(
                API_URL,
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            )
            if r.status_code >= 400:
                raise Exception(
                    f"[SendGridAlerter] sending alert email via HTTP returned code {r.status_code} and body:\n{r.text}"
                )

        except:
            traceback.print_exc()
