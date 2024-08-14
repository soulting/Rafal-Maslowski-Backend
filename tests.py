import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

print(os.getenv('FROM_EMAIL'))

def send_email(subject, body):
    from_email = os.getenv('FROM_EMAIL')
    password = os.getenv('EMAIL_PASSWD')
    smtp_server = os.getenv('SMTP_SERVER')
    port = 587

    # Tworzenie wiadomości e-mail
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = os.getenv('TO_EMAIL')
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # with smtplib.SMTP(smtp_server, port) as server:
    #     server.starttls()  # Używa TLS dla bezpieczeństwa
    #     server.login(from_email, password)
    #     server.send_message(msg)

    try:
        # Połączenie z serwerem SMTP
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, os.getenv('TO_EMAIL'), msg.as_string())
        server.quit()

        return "E-mail wysłany pomyślnie!"
    except Exception as e:
        return f"Błąd: {e}"



print(send_email("temat", 'tresc'))