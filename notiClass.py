class eNotification:
    def __init__(self, env_path = "/home/pi/cam/mess/.env"):
        print('Initialising email notifications')
        import dotenv
        keys = dotenv.Dotenv(env_path)
        self.SMTP_SERVER = keys['SERVER']
        self.SMTP_PORT = int(keys['PORT'])
        self.USERNAME = keys['ADDRESS']
        self.PASSWORD = keys['APIKEY']
        self.RECEIVER = keys['RECEIVER']

    def notify_wImage(self, subject, content, img_path=['/home/pi/cam/still/movem.jpg']):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        import os

        msg = MIMEMultipart()
        msg['From'] = self.USERNAME
        msg['To'] = self.RECEIVER
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))

        for img in range(len(img_path)):
            bname = os.path.basename(img_path[img])
            unit = MIMEBase('application', 'octate-stream')
            unit.set_payload(open(img_path[img], 'rb').read())
            encoders.encode_base64(unit)  # encode the attachment
            unit.add_header('Content-Disposition', f'attachment; filename= {bname}')
            msg.attach(unit)
        # payload = MIMEBase('application', 'octate-stream')
        # payload.set_payload(open(img_path, 'rb').read())
        # encoders.encode_base64(payload)  # encode the attachment
        # payload.add_header('Content-Disposition', f'attachment; filename= {img_fname}')
        # msg.attach(payload)

        session = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
        session.starttls()
        session.login(self.USERNAME, self.PASSWORD)
        text = msg.as_string()
        session.sendmail(self.USERNAME, self.RECEIVER, text)
        session.quit()
        print('email sent')