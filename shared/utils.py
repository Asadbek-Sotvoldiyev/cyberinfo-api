import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from decouple import config
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
        gmail_address = config("EMAIL")
        gmail_password = config("EMAIL_PASSWORD", cast=str)
        to_address = email

        html_body = f"""<!DOCTYPE html>
        <html lang="uz">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cyberinfo.uz - Tasdiqlash</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background-color: #1a73e8;
                    color: #ffffff;
                    padding: 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 20px;
                    text-align: center;
                }}
                .code-box {{
                    background-color: #e8f0fe;
                    padding: 15px;
                    border-radius: 5px;
                    font-size: 24px;
                    font-weight: bold;
                    color: #1a73e8;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
                a {{
                    color: #1a73e8;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Cyberinfo.uz</h1>
                    <p>Kiberxavfsizlik yangiliklari sayti</p>
                </div>
                <div class="content">
                    <h2>Salom!</h2>
                    <p>Siz Cyberinfo.uz saytida ro‘yxatdan o'tishga harakat qildingiz. Quyidagi tasdiqlash kodingizni ishlatib, hisobingizni faollashtiring:</p>
                    <div class="code-box">{code}</div>
                    <p>Agar bu siz bo‘lmasangiz, ushbu xabarni e’tiborsiz qoldiring.</p>
                </div>
                <div class="footer">
                    <p>Hurmat bilan, <a href="https://cyberinfo.uz">Cyberinfo.uz</a> jamoasi</p>
                    <p>&copy; 2025 Cyberinfo.uz. Barcha huquqlar himoyalangan.</p>
                </div>
            </div>
        </body>
        </html>"""

        message = MIMEMultipart()
        message['From'] = f"Cyberinfo.uz <{gmail_address}>"
        message['To'] = to_address
        message['Subject'] = 'Cyberinfo.uz - Tasdiqlash kodi'

        message.attach(MIMEText(f"Tasdiqlash kodi: {code}", 'plain'))
        message.attach(MIMEText(html_body, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmail_address, gmail_password)

            server.sendmail(gmail_address, to_address, message.as_string())
            server.quit()
            
            print("Email muvaffaqiyatli jo‘natildi!")

            time.sleep(5)

        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
