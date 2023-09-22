import requests
import traceback
from datetime import datetime
from app.AggroConfig import AggroConfigEmailAlerter
from dataclasses import asdict


class EmailAlerter:
    @staticmethod
    def from_config(config: AggroConfigEmailAlerter) -> "EmailAlerter":
        return EmailAlerter(**asdict(config))

    def __init__(
        self, api_url: str, api_auth: str, email_from: str, email_to: list[str]
    ):
        self.api_url = api_url
        self.email_from = email_from
        self.email_to = email_to
        api_auth_parts = api_auth.split(":")
        if len(api_auth_parts) != 2:
            raise Exception(
                "[EmailAlerter] supplied api_auth is not of form <key>:<value>"
            )
        self.api_auth = (api_auth_parts[0], api_auth_parts[1])

    def send_alert(self, text: str):
        try:
            now = datetime.now()
            now_text = now.strftime("%a, %d %b %Y %H:%M:%S +0000")
            data = {
                "from": self.email_from,
                "to": self.email_to,
                "subject": f"Aggro alert on {now_text}",
                "text": text,
            }
            r = requests.post(
                self.api_url,
                auth=self.api_auth,
                data=data,
            )
            if r.status_code >= 400:
                raise Exception(
                    f"[EmailAlerter] sending alert email via HTTP returned code {r.status_code} and body:\n{r.text}"
                )

        except:
            traceback.print_exc()
