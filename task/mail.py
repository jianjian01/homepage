import logging
import time

from pony.orm import db_session, set_sql_debug

from db import UserMailHistory, User, UserMailCategory
from flask_app import redis, flask_app

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


@db_session
def send_email_verify_url(user_id, name, email, url):
    """发送验证邮箱的链接"""
    logging.info('mail.send_email_verify_url')
    conf = flask_app.config
    if user_id.isdigit():
        user_id = int(user_id)
    else:
        logging.warning("数据错误， {}".format(user_id))
        return

    subject = '吃点心 - 账户激活'
    content = template.format(name, url)
    user = User.select(lambda x: x.u_id == user_id)
    if not user:
        time.sleep(5)
        user = User.select(lambda x: x.u_id == user_id)
        if not user:
            logging.warning("用户创建失败， {}".format(user_id))
            return
    UserMailHistory(user=user.first(), address=email, content=content,
                    category=UserMailCategory.verify_email)
    send_mail(host=conf['SMTP_HOST'], port=conf['SMTP_PORT'],
              email_address=conf['SMTP_EMAIL'], password=conf['SMTP_PASSWORD'],
              to_address=email, subject=subject, content=content)


def main():
    conf = flask_app.config
    while 1:
        item = redis.xread({conf['REDIS_VERIFY_EMAIL_CHANNEL']: '$'}, 1, 0)
        logging.info(item)
        data = item[0][1][0][1]
        time.sleep(10)
        send_email_verify_url(data[b'user_id'].decode(), data[b'name'].decode(),
                              data[b'email'].decode(), data[b'url'].decode())


if __name__ == '__main__':
    main()
