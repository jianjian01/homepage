import random
from datetime import datetime

from pony.orm import Database, Required, set_sql_debug, PrimaryKey, Optional, Set, select, LongStr

db = Database()


# set_sql_debug(True)


class UserStatus:
    delete = -1
    not_exist = 0
    normal = 1


class UserSource:
    github = 1
    weibo = 2


class User(db.Entity):
    """用户"""
    id = PrimaryKey(int, auto=True)
    u_id = Required(int, unique=True, py_check=lambda x: User.id_min < x < User.id_max)
    name = Required(str)
    email = Optional(str)
    source = Required(int)
    source_id = Required(str)
    source_data = Optional(LongStr)

    sites = Set(lambda: UserSite)
    categories = Set(lambda: Category)
    mails = Set(lambda: UserMailHistory)

    status = Required(int, default=UserStatus.normal)
    create_time = Required(datetime, default=datetime.utcnow)
    last_login_time = Required(datetime, default=datetime.utcnow)

    # 生成自定义 ID
    id_min = 100000000
    id_max = 999999999

    @staticmethod
    def new_uid():
        """生成新的用户ID"""
        while 1:
            n_id = random.randint(User.id_min, User.id_max)
            if not User.select(lambda c: c.u_id == n_id):
                return n_id

    @staticmethod
    def email_status(email):
        """检查邮件地址状态"""
        user = User.select(lambda c: c.email == email and c.status != UserStatus.delete)
        if user:
            return user.first().status
        return UserStatus.not_exist


class Site(db.Entity):
    """网站信息"""
    id = PrimaryKey(int, auto=True)
    host = Required(str, unique=True, index=True)
    icon = Optional(str, unique=True)


class Category(db.Entity):
    """分类"""
    id = PrimaryKey(int, auto=True)
    name = Required(str, index=True)
    user = Required(User)
    hide = Required(bool, default=False)
    delete = Required(bool, default=False)
    sites = Set(lambda: UserSite)


class UserSiteStatus:
    normal = 1
    delete = 0


class UserSite(db.Entity):
    """用户保存网站信息"""
    id = PrimaryKey(int, auto=True)
    url = Required(str)
    user = Required(User)
    cate = Optional(Category)
    header = Required(bool, default=False)

    create_time = Required(datetime, default=datetime.utcnow)
    status = Required(int, default=UserSiteStatus.normal)
    delete_time = Optional(datetime)


class UserMailCategory:
    """发送给用户的邮件种类"""
    verify_email = 1


class UserMailHistory(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    address = Required(str)
    content = Required(LongStr, sql_type='text')
    category = Required(int)
    create_time = Required(datetime, default=datetime.utcnow)
    status = Required(int, default=UserSiteStatus.normal)


if __name__ == '__main__':
    db.bind(provider='mysql',
            user='root', passwd='8W5Qqv9IfgdvHk',
            host='47.96.177.79', port=29898,
            db='chidianxin')
    db.generate_mapping(create_tables=True)
