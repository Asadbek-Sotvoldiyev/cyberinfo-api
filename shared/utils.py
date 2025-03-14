import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from rest_framework.exceptions import ValidationError

email_regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
username = re.compile(r"^[a-zA-Z0-9._-]+$")
phone_regex = re.compile(r"^\+998[0-9]{9}$")


def check_user_type(user_input):
    if re.fullmatch(email_regex, user_input):
        user_input = 'email'
    elif re.fullmatch(username, user_input):
        user_input = 'username'
    elif re.fullmatch(phone_regex, user_input):
        user_input = 'phone'
    else:
        data = {
            "success": False,
            "message": "Email, Telefon raqam yoki Username xato"
        }
        raise ValidationError(data)
    return user_input


def check_email(email):
    if re.fullmatch(email_regex, email):
        return True
    else:
        data = {
            "success": False,
            "message": "Email xato kiritildi. Qayta yuboring..."
        }
        raise ValidationError(data)


def send_email(email, code):
    if check_email(email):
        gmail_address = "blogasadbek@gmail.com"
        gmail_password = "nbsy knzw pdlc wkqt "
        to_address = email
        message = MIMEMultipart()
        message['From'] = gmail_address
        message['To'] = to_address
        message['Subject'] = 'Cyberinfo.uz confirmation'
        body = f"Salom! Sizning tasdiqlash kodingiz: {code}"
        message.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_address, gmail_password)
        server.sendmail(gmail_address, to_address, message.as_string())

        server.quit()
