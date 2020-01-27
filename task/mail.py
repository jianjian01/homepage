from celery import current_app as celery_app
from flask import current_app as current_flask
from pony.orm import select, db_session, set_sql_debug, commit

from util.mail import send_mail

set_sql_debug(True)

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


@celery_app.task(name="send_email_verify_url")
@db_session
def send_email_verify_url(name, email, url):
    """发送验证邮箱的链接"""
    conf = current_flask.config
    subject = '吃点心 - 账户激活'
    content = template.format(name, url)
    send_mail(host=conf['SMTP_HOST'], port=conf['SMTP_PORT'],
              email_address=conf['SMTP_EMAIL'], password=conf['SMTP_PASSWORD'],
              to_address=email, subject=subject, content=content)
