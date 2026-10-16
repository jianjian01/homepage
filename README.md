# 个人主页

## 网站收藏
1. 设置分组，添加网址。默认存在一个没有名称的分组，
2. 分组和网址都有序号，用来排序。
3. 控制台点击网址的 icon 能设置新的 icon。

## RSS 
考虑到用户可能会订阅相同的 RSS 源，避免重复请求 RSS 源，这里设计多个表。

RSS 表，保存所有的 RSS 链接，独立的一张表。

PAGE 表，保存所有 RSS 获取到的文章，只保存基础信息，不保存文章内容，只和 RSS 表关联。

USERRSS 表，用户订阅 RSS 的记录表，当用户添加一个 RSS 源的时候，查询 RSS 表中记录是否存在，如果不存在，则添加，如果存在，则直接保存记录。查询时，根据关系表，查询 PAGE 表，获取所有文章。

### rss 索引 ###
`atoma` 、`feedparser` 似乎都不太靠谱，这里使用 `feedparser` ，如果抛出异常，在使用 `atoma`

## 国际化 ##

```shell script
# 查找翻译文件
pybabel extract -F babel.cfg -o messages.pot .
# 初始化语言文件夹，zh ja en ...
pybabel init -i messages.pot -d translations -l zh
# 更新文件夹
pybabel update -i messages.pot -d translations
# 翻译之后，编译一下才能使用
pybabel compile -d translations
```

## 运行

```shell
cp .env.example .env
# 填写已有的数据库密码、Flask SECRET_KEY 和 OAuth 配置
mkdir -p data/mysql logs static/site nginx/cloudflare
# 将源站证书和私钥分别放入 nginx/cloudflare/dooest.com.pem 和 dooest.com.key
docker compose up -d --build
```

Compose 包含 MySQL、Redis、Web、RSS 抓取、图标下载和 Nginx。MySQL 数据库及
`myweb` 应用账号需要事先初始化或从备份恢复；`MYSQL_PASSWORD` 必须与应用账号一致。
`.env`、数据库文件、用户图标及证书私钥不会提交到 Git，也不会复制进镜像。

生产目录为 `/home/ubuntu/dooest`，应用代码位于其 `myweb100/` 子目录。仓库根目录
对应生产的 `myweb100/`，仓库中的 `docker-compose.yml` 和 `nginx/conf.d/` 则对应
生产外层目录中的同名文件。沿用该布局时，将部署文件放到外层目录，并在外层
`.env` 设置 `APP_SOURCE_DIR=./myweb100`；普通仓库检出保留默认值 `.`。

生产已有的 `config.py` 使用内联凭据。本次提交的配置改为读取环境变量：后续部署
这份代码时，先把原有值填写到外层 `.env`，保留原 `SECRET_KEY`，再更新 Compose、
构建镜像并重新创建服务。仅替换配置而未提供环境变量会导致数据库连接或登录异常。

Nginx 实际使用 `nginx/conf.d/dooest.com.conf`，静态文件挂载到
`/static/myweb100/static`，配置中的 `root` 必须与该路径一致。
页面引用 `/js/base.js`、`/js/user/rss.js` 和 `/js/user/website.js`；静态路径错误会使
这些脚本返回 404，导致 RSS 和网站管理按钮无法响应。

修改 Nginx 配置后检查并平滑重载：

```shell
docker compose exec nginx nginx -t
docker compose exec nginx nginx -s reload
```

Web 的模板和 Python 代码主要构建在镜像中；修改后需要重新构建并创建相关容器，
单独重启容器不会更新镜像中的代码。Nginx 配置和静态目录则通过绑定挂载读取。


