import pymongo
from flask import Blueprint
import arrow
import jieba

from utils.auth_helper import *
from utils.return_result import *

news = Blueprint('news', __name__)


@news.route('/news/list', methods=['GET'])
@require_token
def get_news_list(login_user) -> str:
    f = request.args
    query_conditions = {}
    request_type = f['type']
    sort_by_date = True

    if request_type == 'timeline':
        query_conditions['channel_id'] = {
            '$in': login_user['subscription']
        }

        if 'before_time' in f.keys() or 'after_time' in f.keys():
            query_conditions['pubdate'] = {}

        if 'before_time' in f.keys():
            before_time = arrow.get(f['before_time']).to("UTC").datetime
            query_conditions['pubdate']['$lt'] = before_time

        if 'after_time' in f.keys():
            after_time = arrow.get(f['after_time']).to("UTC").datetime
            query_conditions['pubdate']['$gte'] = after_time

    elif request_type == 'channel':
        query_conditions['channel_id'] = int(f['channel_id'])

    elif request_type == 'favorite':
        query_conditions['_id'] = {
            '$in': login_user['favorite']
        }

    elif request_type == 'search':
        query_conditions['$text'] = {
            '$search': ' '.join(jieba.lcut(f['query']))
        }

    elif request_type == 'recommend':
        if 'recommend' in login_user.keys():
            sort_by_date = False
            query_conditions['_id'] = {
                '$in': login_user['recommend']
            }
        else:
            ok([])

    else:
        return error(ErrorCause.REQUEST_INVALID, 'Cannot get news of type ' + request_type)

    if 'count' in f.keys():
        page_count = int(f['count'])
    else:
        page_count = 20

    if 'page' in f.keys():
        page = int(f['page'])
        if not page >= 0:
            page = 0
    else:
        page = 0

    cursor = db.news.find(query_conditions)

    if sort_by_date:
        cursor = cursor.sort("pubdate", pymongo.DESCENDING)

    results = list(cursor.skip(page * page_count).limit(page_count))

    for news_item in results:
        news_item['pubdate'] = news_item['pubdate'].isoformat()
        news_item['comment_num'] = db.comments.find({
            'news_id': news_item['_id']
        }).count()
        if 'likes' in news_item.keys():
            news_item['like_num'] = len(news_item['likes'])
            del news_item['likes']
        else:
            news_item['like_num'] = 0

        all_read_info = db.statistics.find({
            'news_id': news_item['_id']
        })

        news_item['read_num'] = all_read_info.count()

        read_info = db.statistics.find_one({
            'news_id': news_item['_id'],
            'user_id': login_user['_id']
        })
        news_item['has_read'] = read_info is not None

    return ok(results)


@news.route('/news/detail', methods=['GET'])
@require_token
def get_news_detail(login_user) -> str:
    news_id = int(request.args['news_id'])

    news_item = db.news.find_one({
        '_id': news_id
    })

    if news_item is None:
        return error(ErrorCause.CONTENT_NOT_EXISTED, "News {} does not exist".format(news_id))

    db.statistics.insert_one({
        'user_id': login_user['_id'],
        'news_id': news_id,
        'time': arrow.utcnow().datetime
    })

    comments = list(db.comments.aggregate([
        {
            '$match': {'news_id': news_item['_id']}
        },
        {
            '$lookup': {
                'from': 'Users',
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'user_info'
            }
        },
        {
            '$unwind': '$user_info'
        },
        {
            '$addFields': {'username': '$user_info.username'}
        }
    ]))

    for comment in comments:
        comment['time'] = comment['time'].isoformat()
        del comment['user_info']
        del comment['user_id']
        del comment['news_id']

    news_detail = {
        'like': 'likes' in news_item.keys() and login_user['_id'] in news_item['likes'],
        'favorite': news_item['_id'] in login_user['favorite'],
        'comments': comments
    }

    return ok(news_detail)


@news.route('/news/like', methods=['PUT', 'DELETE'])
@require_token
def manage_favorite(login_user) -> str:
    user_id = login_user['_id']
    news_id = request.json['news_id']

    news_item = db.news.find_one({
        '_id': news_id
    })

    if news_item is None:
        return error(ErrorCause.CONTENT_NOT_EXISTED, 'News {} does not exist'.format(news_id))

    if 'likes' in news_item.keys():
        like_users = news_item['likes']
    else:
        like_users = []

    if request.method == 'PUT':
        if user_id not in like_users:
            like_users.append(user_id)
    elif request.method == 'DELETE':
        if user_id in like_users:
            like_users.remove(user_id)

    db.news.update_one({
        '_id': news_id
    }, {'$set': {
        'likes': like_users
    }})

    return ok()
