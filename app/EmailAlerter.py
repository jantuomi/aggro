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
        self,
        api_url: str,
        api_headers: dict[str, str],
        email_from: str,
        email_to: list[str],
    ):
        self.api_url = api_url
        self.email_from = email_from
        self.email_to = email_to
        self.api_headers = api_headers

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
                data=data,
                headers=self.api_headers,
            )
            if r.status_code >= 400:
                raise Exception(
                    f"[EmailAlerter] sending alert email via HTTP returned code {r.status_code} and body:\n{r.text}"
                )

        except:
            traceback.print_exc()
