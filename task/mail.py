from celery import current_app as celery_app
from celery.utils.log import get_task_logger
from flask import current_app as current_flask

from util.mail import send_mail

template = """<html lang="zh">
<body>
<p>亲爱的用户 {}:</p>
<br/>
<p>&nbsp;&nbsp;&nbsp;&nbsp;您的账户激活地址: {}。<small>如果无法点击，请复制到浏览器打开。</small> </p>
<br/>
<p>感谢您的注册，祝您使用愉快！</p>
<p>吃点心团队</p>
</body>
</html>"""

logger = get_task_logger(__name__)


@celery_app.task(name="mail.send_email_verify_url")
def send_email_verify_url(name, email, url):
    """发送验证邮箱的链接"""
    logger.info('mail.send_email_verify_url')
    conf = current_flask.config
    subject = '吃点心 - 账户激活'
    content = template.format(name, url)
    send_mail(host=conf['SMTP_HOST'], port=conf['SMTP_PORT'],
              email_address=conf['SMTP_EMAIL'], password=conf['SMTP_PASSWORD'],
              to_address=email, subject=subject, content=content)


@celery_app.task
def test():
    print('abc')
