from email.mime.text import MIMEText
from smtplib import SMTP_SSL


def send_mail(host, port, email_address, password, to_address, subject, content):
    """
    发送邮件
    :return:
    """
    smtp = SMTP_SSL(host=host, port=port)
    smtp.login(email_address, password)
    msg = MIMEText(content, 'html', 'utf-8')

    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = to_address
    smtp.send_message(msg)
    smtp.close()

