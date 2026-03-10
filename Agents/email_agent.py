import os
from typing import Dict

import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, To
from agents import Agent, function_tool

@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send an email with the given subject and HTML body"""
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email(os.environ.get("SENDGRID_FROM_EMAIL"))  # sendgrid verified sender 
    to_email = To(os.environ.get("SENDGRID_TO_EMAIL"))  # recipient
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print("Email response", response.status_code)
    return {"status": "success"}


INSTRUCTIONS = """You are capable of sending a well-formatted HTML email based on a detailed report.
You will receive the report as input. Your task is to generate a single email that includes:

1. The report content converted into clean, structured, and visually appealing HTML.
2. An appropriate subject line that clearly reflects the report's content.

Ensure the email is professional, readable, and suitable for recipients who need to quickly grasp the report's key information."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
