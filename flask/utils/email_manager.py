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
        self.sender_email_address = config.GMAIL_ADDRESS
        self.sender_email_password = config.GMAIL_APP_PASSWORD

    def send_email(self, receiver_email_address: str, subject: str, text: str):
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

    def send_two_factor_authentication_code(self, id:int, code:int):

        name = database_handler.get_name_from_id(id=id)
        receiver_email_address = database_handler.get_email_from_id(id=id)
        
        text = f'''
        Hello {name},\n
        Your two-factor login code:\n
        {code}\n
        You recently tried to log in from a new device, browser, or location.
        To log in, please use the code above.								 		
        If this wasn't you, please change your password.\n
        Thank you!
        '''

        message = MIMEText(text, "plain")
        message["Subject"] = "Two-factor authentication code"
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

    def send_two_factor_authentication_code_with_html(self, id:int, code:int):

        name = database_handler.get_name_from_id(id=id)
        receiver_email_address = database_handler.get_email_from_id(id=id)

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

        message = MIMEMultipart()
        message["Subject"] = "Two-factor authentication code"
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

        except Exception as e:
            print("Erreur send_email() :", e)