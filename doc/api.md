# API 设计

本项目实现前后端分离，前端向后端通过 API 请求实现数据交互。计划的 API 如下：

## 通用说明

### 请求格式

所有交互都是 JSON 格式。

用户请求如果注明为需要认证，则自动带上 HTTP Header "Authorization"，内容为获得的 Access Token。

服务器的返回值有如下两种格式：

请求失败：

| 名称          | 类型   | 说明                 |
| ------------- | ------ | -------------------- |
| error_code    | int    | 失败代码             |
| error_message | string | 失败原因             |
| reason        | string | 具体解释（可能为空） |

请求成功：

| 名称       | 类型           | 说明     |
| ---------- | -------------- | -------- |
| error_code | int            | 一定为 0 |
| result     | object / array | 请求结果 |

### 错误代码

| 错误代码（error_code） | 错误消息（error_message) | 其他说明                           |
| ---------------------- | ------------------------ | ---------------------------------- |
| 1                      | Not Authorized           | 请求了一个需要认证的接口但未认证   |
| 2                      | Login Failed             | 登录失败                           |
| 3                      | User Existed             | 注册的用户名重复                   |
| 4                      | Not Existed              | 请求的内容（频道/新闻/评论）不存在 |
| 5                      | No More Content          | 没有更多内容                       |
| 6                      | Request Invalid          | 非法请求                           |
| 7                      | Request Incomplete       | 请求不完整                         |

## 用户管理

### 注册与登录

```raw
POST /user/login
```

需要认证：否

请求参数：

| 名称     | 必选 | 类型   | 说明     |
| -------- | ---- | ------ | -------- |
| username | 是   | string | 用户名称 |
| password | 是   | string | 用户密码 |
| register | 否   | bool   | 是否注册 |

如果密码为空，或者用户名已经存在，或者用户名不合法，都会返回对应的错误。

返回值：



| 名称  | 类型   | 说明                |
| ----- | ------ | ------------------- |
| token | string | 用户的 Access Token |

说明：

注册和登录成功均会返回 Token，前者可用于自动登录。

## 内容获取

## 频道获取

```
GET /channel/list
```

需要认证：是

请求参数：无

返回值示例：

```json
{
    "categories": [
        {
            "_id": 1,
            "name": "新闻频道",
            "channels": [
                {
                    "_id": 1,
                    "name": "国内新闻",
                    "description": "国内时政新闻、各地新闻及综述评论",
                    "subscribed": true
                },
                {
                    "_id": 2
                    "name": "国际新闻",
                    "description": "世界新闻报道",
                    "subscribed": false
                }
            ]
        }
    ]
}
```

其中 `subscribed` 表示用户是否订阅了该频道。Category 和 Channel 的 ID 各自都是全局唯一的。

## 新闻获取

```
GET /news/list
```

需要认证：是

请求参数：

| 名称        | 必选 | 类型                    | 说明                                       |
| ----------- | ---- | ----------------------- | ------------------------------------------ |
| type        | 是   | string                  | "timeline"/"favorite"/"search"/"recommend" |
| channel_id  | 否   | int                     | 指定频道的 id                              |
| before_time | 否   | string（ISO 8601 Time） | 最晚发布时间（不含）                       |
| after_time  | 否   | string（ISO 8601 Time） | 最早发布时间（含）                         |
| query       | 否   | string                  | 搜索的关键词                               |
| count       | 否   | int                     | 每页新闻数量（默认20，最大 100）           |
| page        | 否   | int                     | 页码（默认为0）                            |

四个 type 分别代表：正常时间轴，查询收藏的新闻、搜索新闻和查看推荐。如果 type 是非法的，会返回错误。在非 timeline 模式下， channel_id 和时间限制都是无效的。在 timeline 模式中，如果指定了 channel_id （即查看某个特定频道），即使用户没有订阅这个频道，也会返回消息。如果没有查询到内容，比如请求的页码超过了总的可用页码，或者收藏为空/搜索失败，会返回错误（见上）。

返回值示例：

```json
{
    "news": [
        {
            "_id": 42,
            "channel_id": 10,
            "title": "山东省政府：超强降雨是洪灾主因，潍坊市水库调度符合规定",
            "summary": "国家防汛抗旱总指挥部办公室专家组专家组认为，一周内连续2次超强降雨是造成洪涝灾害的主要原因，潍坊市水库调度做到了提前预警，最后一次预警较洪峰到达提前6小时，使受威胁群众能够及时转移，水库调度符合调度方案规定。",
            "comments_num": 2,
            "like_num": 1023,
            "author": "www.qq.com",
            "pubdate": "2018-08-29T17:43:26+08:00",
            "link": "http://news.qq.com/a/20180829/077120.htm",
            "picture": ""
        },
        {
            "_id": 128,
            "channel_id": 10,
            "title": "今年中国规模最大的主场外交！聚焦中非合作论坛北京峰会四个看点",
            "summary": "新华社北京8月29日电题：今年中国规模最大的主场外交！聚焦中非合作论坛北京峰会四个看点新华社“新华视点”记者伍岳、许可、乌梦达2018年中非合作论坛北京峰会将于9月3日至4日举行。届时，中非领导人将齐聚北京，围绕“合作共赢，携手构建更加紧密的中非命运共同体”主题，规划新时期中非合作“路线图”。作为今年中国举",
            "comments_num": 0,
            "like_num": 14,
            "author": "www.qq.com",
            "pubdate": "2018-08-29T12:52:26+08:00",
            "link": "http://news.qq.com/a/20180829/054519.htm",
            "picture": "https://inews.gtimg.com/newsapp_bt/0/5039464058/641"
        }
    ]
}
```

保证返回的 News 的 ID 是全局唯一的。在 timeline 和 search 模式下，结果按照新闻发布时间降序排列；在 favorite 模式下，结果按照收藏的时间降序排列。

### 新闻详情获取

```
GET /news/detail
```

需要认证：是

请求参数：

| 名称    | 必选 | 类型 | 说明    |
| ------- | ---- | ---- | ------- |
| news_id | 是   | int  | 新闻 id |

如果指定的新闻不存在，会返回错误。

返回值示例：

```json
{
    "like": false,
    "favorite": true,
    "keywords": [
                "foo", "bar"
    ],
    "comments": [
        {
            "_id": 2,
            "username": "shanker",
            "content": "是好人。。是好人。。。",
            "time": "2018-08-28T08:08:08+08:00"
        },
        {
            "_id": 4,
            "username": "jiegec",
            "content": "让我看看",
            "time": "2011-04-05T14:08:10+09:00"
        }
    ]
}
```

如果没有评论，会返回空数组。

## 内容更改

### 订阅管理

```
PUT /channel/subscribe
DELETE /channel/subscribe
```

需要认证：是

请求参数：

| 名称        | 必选 | 类型  | 说明    |
| ----------- | ---- | ----- | ------- |
| channel_ids | 是   | int[] | 频道 id |

如果请求的任何频道不存在，则会返回错误。

如果取消订阅未订阅频道，或者重复订阅频道，则不会产生错误。

### 收藏管理

```
PUT /user/favorite
DELETE /user/favorite
```

需要认证：是

请求参数：

| 名称     | 必选 | 类型  | 说明    |
| -------- | ---- | ----- | ------- |
| news_ids | 是   | int[] | 新闻 id |

如果请求的新闻不存在，则会返回错误。

如果删除一个不存在的收藏，或者反复收藏同一条新闻，则不会产生错误。

### 点赞管理

```
PUT /news/like
DELETE /news/like
```

需要认证：是

请求参数：

| 名称    | 必选 | 类型 | 说明    |
| ------- | ---- | ---- | ------- |
| news_id | 是   | int  | 新闻 id |

如果请求的新闻不存在，则会返回错误。

如果取消一个不存在的点赞，或者反复点赞同一条新闻，则不会产生错误。

### 添加评论

```
POST /news/comment
```

需要认证：是

请求参数：

| 名称    | 必选 | 类型   | 说明     |
| ------- | ---- | ------ | -------- |
| news_id | 是   | int    | 新闻 id  |
| content | 是   | string | 评论内容 |

如果指定的新闻不存在或者内容为空，会返回错误。

返回值示例：

```json
{
    "_id": 11,
    "username": "xavier",
    "content": "支持！",
    "time": "2018-09-17T07:15:12+08:00"
}
```

### 删除评论

```
DELETE /news/comment
```

需要认证：是

请求参数：

| 名称       | 必选 | 类型 | 说明    |
| ---------- | ---- | ---- | ------- |
| news_id    | 是   | int  | 新闻 id |
| comment_id | 是   | int  | 评论 id |

如果请求的新闻或者评论不存在，则会返回错误。