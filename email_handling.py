import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def send_email(subject, body):
    from_email = os.getenv("FROM_EMAIL")
    to_email = os.getenv("TO_EMAIL")
    password = os.getenv("EMAIL_PASSWD")
    smtp_server = os.getenv("SMTP_SERVER")
    port = 587

    # Tworzenie wiadomości e-mail
    msg = MIMEMultipart()
    msg["From"] = "Rafał Masłowski Portfolio"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Połączenie z serwerem SMTP
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        return "E-mail wysłany pomyślnie!"
    except Exception as e:
        return f"Błąd: {e}"
