import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from Data.database_handler import DatabaseHandler

database_handler = DatabaseHandler()
config = Config()

class EmailManager:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email_address = config.EMAIL_ADDRESS
        self.sender_email_password = config.EMAIL_APP_PASSWORD

    def get_hide_email(self, user_id:int) -> (str|None):
        receiver_email_address = database_handler.get_email_from_id(id=user_id)
        if receiver_email_address is None:
            return None
        
        email = str(receiver_email_address)
        at_index = email.index('@')

        number_char_visible = 3
        visible = email[:number_char_visible]
        domain = email[at_index:]

        hidden_length = max(at_index - number_char_visible, 0)
        hidden = '*' * hidden_length

        return visible + hidden + domain

    def send_email(self, receiver_email_address:str, subject:str, text:str):
        message = MIMEText(text, "plain")
        message["Subject"] = subject
        message["From"] = self.sender_email_address
        message["To"] = receiver_email_address

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.sender_email_address, self.sender_email_password)
                server.sendmail(
                    self.sender_email_address,
                    receiver_email_address,
                    message.as_string()
                )

            print(f"Email sent {receiver_email_address}")

        except Exception as e:
            print("Erreur send_email() :", e)

    def send_email_with_html_content(self, user_id:int, subject:str, html_content:str):
        receiver_email_address = database_handler.get_email_from_id(id=user_id)

        if receiver_email_address is None:
            return False
        
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = self.sender_email_address
        message["To"] = receiver_email_address

        # Attach the HTML part
        message.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.sender_email_address, self.sender_email_password)
                server.sendmail(
                    self.sender_email_address,
                    receiver_email_address,
                    message.as_string()
                )

            print(f"Email sent {receiver_email_address}")
            return True

        except Exception as e:
            print("Erreur send_email() :", e)
            return False

    def send_two_factor_authentication_code_with_html(self, user_id:int, code:int):
        name = database_handler.get_name_from_id(id=user_id)
        receiver_email_address = database_handler.get_email_from_id(id=user_id)

        if receiver_email_address is None:
            return False

        subject = "Two-factor authentication code"
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#FAFAF8;">
            <div style="
                max-width:600px;
                margin:40px auto;
                padding:30px;
                background:#ffffff;
                border-radius:10px;
                box-shadow:0 4px 10px rgba(0,0,0,0.1);
                text-align:center;
            ">
                <h1 style="color:#9B7ED8;">Hello {name}</h1>

                <p style="font-size:16px; color:#333;">
                    Your two-factor authentication code:
                </p>

                <p style="
                    font-size:32px;
                    font-weight:bold;
                    letter-spacing:6px;
                    color:#9B7ED8;
                    margin:20px 0;
                ">
                    {code}
                </p>

                <p style="font-size:14px; color:#555;">
                    You recently tried to log in from a new device, browser, or location.
                    <br><br>
                    If this wasn't you, please change your password immediately.
                </p>

                <p style="font-size:12px; color:#999; margin-top:30px;">
                    - Titou Service Security Team -
                </p>
            </div>
        </body>
        </html>
        """
        return self.send_email_with_html_content(user_id=user_id, subject=subject, html_content=html_content)
        
    def send_new_password_code_with_html(self, user_id:int, new_password:int):
        name = database_handler.get_name_from_id(id=user_id)
        receiver_email_address = database_handler.get_email_from_id(id=user_id)

        if receiver_email_address is None:
            return False
        
        subject = "New Password"
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#FAFAF8;">
            <div style="
                max-width:600px;
                margin:40px auto;
                padding:30px;
                background:#ffffff;
                border-radius:10px;
                box-shadow:0 4px 10px rgba(0,0,0,0.1);
                text-align:center;
            ">
                <h1 style="color:#9B7ED8;">Hello {name}</h1>

                <p style="font-size:16px; color:#333;">
                    Here your new password :
                </p>

                <p style="
                    font-size:20px;
                    font-weight:bold;
                    color:#9B7ED8;
                    margin:20px 0;
                ">
                    {new_password}
                </p>

                <p style="font-size:16px; color:#333;">
                    You can log in on the login page. Remember to change your password afterwards. 
                </p>

                <p style="font-size:14px; color:#555;">
                    You recently tried to log in from a new device, browser, or location.
                    <br><br>
                    If this wasn't you, please change your password immediately.
                </p>

                <p style="font-size:12px; color:#999; margin-top:30px;">
                    - Titou Service Security Team -
                </p>
            </div>
        </body>
        </html>
        """
        return self.send_email_with_html_content(user_id=user_id, subject=subject, html_content=html_content)
