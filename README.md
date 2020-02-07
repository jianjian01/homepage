# dian-xin

## 静态文件 
static.myweb100.com

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
pybabel init -i messages.pot -d translations -l ja
# 更新文件夹
pybabel update -i messages.pot -d translations
# 翻译之后，编译一下才能使用
pybabel compile -d translations
```

