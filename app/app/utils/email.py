"""
Simple email utility used by automations.

In Nexora V1, actual email delivery is not implemented due to
environment constraints.  Instead, this module logs the email
parameters to the console.  To integrate with a real email provider,
replace the `send_email` function with calls to an SMTP client or
third‑party service.
"""

import logging
from typing import List


def send_email(to: List[str] | str, subject: str, body: str) -> None:
    """Simulate sending an email by logging.

    Args:
        to: Recipient address or list of addresses.
        subject: Subject line of the email.
        body: Plain text body of the email.
    """
    recipients = to if isinstance(to, list) else [to]
    logging.info("Sending email to %s | subject=%s | body=%s", ", ".join(recipients), subject, body)