import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database import db
from datetime import datetime


def send_email(subject, body, to_email, smtp_data):
    try:
        # print(smtp_data)
        msg = MIMEMultipart()
        msg['From'] = smtp_data['username']
        msg['To'] = to_email['email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP_SSL(smtp_data['host'], smtp_data['port'])

        server.login(smtp_data['username'], smtp_data['password'])

        server.sendmail(smtp_data['username'], to_email['email'], msg.as_string())

        server.quit()

        print("Email sent successfully!")
        db.logs.insert_one({
            "user_id":to_email['user_id'],
            "survey_type": "complete",  # crude extraction for log
            "status": "sent",
            "response": subject + "/n" + body,
            "sent_at": datetime.utcnow()
        })

    except Exception as e:
        print(f"Error: {e}")