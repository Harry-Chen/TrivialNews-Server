# 数据库设计

本项目使用 MongoDB 作为数据库后端，具体表结构如下：

## Users

本表用于存储用户相关信息。

| 列名         | 类型   | 说明                    |
| ------------ | ------ | ----------------------- |
| _id          | int    | 用户 id                 |
| username     | string | 用户名                  |
| password     | string | （哈希后的）密码        |
| token        | string | 当前签发的 Access Token |
| subscription | int[]  | 用户订阅的频道 id       |
| favorite     | int[]  | 用户收藏过的新闻 id     |

## Channels

本表用于存储频道相关信息。

| 列名        | 类型   | 说明     |
| ----------- | ------ | -------- |
| _id         | int    | 频道 id  |
| name        | string | 频道名称 |
| description | string | 频道简介 |

## Categories

本表用于存储大的频道分类。

| 列名     | 类型   | 说明              |
| -------- | ------ | ----------------- |
| _id      | int    | 类别 id           |
| name     | string | 类别名称          |
| channels | int[]  | 该类别下的频道 id |

## News

本表用于存储新闻的详情。

| 列名       | 类型                   | 说明                    |
| ---------- | ---------------------- | ----------------------- |
| _id        | int                    | 新闻 id                 |
| channel_id | int                    | 新闻所在的频道的 id     |
| title      | string                 | 标题                    |
| summary    | string                 | 摘要                    |
| keywords   | string[]               | 抽取的关键词            |
| author     | string                 | 作者                    |
| pubdate    | string (ISO 8601 Time) | 发布时间                |
| link       | string                 | 详细信息链接            |
| picture    | string                 | 新闻题图 URL （如果有） |
| likes      | int[]                  | 给其点赞的用户 id       |

## Statistics

本表用于存储用户对新闻的阅读情况，用作推荐目的。

| 列名    | 类型                   | 说明              |
| ------- | ---------------------- | ----------------- |
| _id     | （不关心）             | 自动生成的唯一 id |
| user_id | int                    | 用户 id           |
| news_id | int                    | 新闻 id           |
| time    | string (ISO 8601 Time) | 阅读时间          |

## Comments

本表用于存储新闻的评论信息。

| 列名    | 类型                   | 说明         |
| ------- | ---------------------- | ------------ |
| _id     | int                    | 评论 id      |
| new_id  | int                    | 新闻 id      |
| user_id | int                    | 用户 id      |
| time    | string (ISO 8601 Time) | 评论发布日期 |
| content | string                 | 内容         |