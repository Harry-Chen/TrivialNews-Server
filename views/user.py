from flask import Blueprint

from utils.auth_helper import *
from utils.misc import generate_token, generate_id, hash_password
from utils.return_result import *

user = Blueprint('user', __name__)


@user.route('/user/login', methods=['POST'])
def login() -> str:
    f = request.json
    if 'register' in f.keys() and f['register']:

        new_user_name = f['username']
        if db.users.find_one({'username': new_user_name}) is not None:
            return error(ErrorCause.USER_EXISTED)

        new_token = generate_token()
        new_user = {
            '_id': generate_id(),
            'username': f['username'],
            'password': hash_password(f['password']),
            'token': new_token,
            'subscription': [],
            'favorite': []
        }

        db.users.insert_one(new_user)

        del new_user['password']
        del new_user['_id']

        return ok(new_user)

    else:

        now_user = db.users.find_one({
            'username': f['username'],
            'password': hash_password(f['password']),
        })

        if now_user is None:
            return error(ErrorCause.LOGIN_FAILED)

        new_token = generate_token()

        db.users.update_one({
            '_id': now_user['_id']
        }, {'$set': {
            'token': new_token
        }})

        now_user['token'] = new_token
        del now_user['password']
        del now_user['_id']

        return ok(now_user)


@user.route('/user/favorite', methods=['PUT', 'DELETE'])
@require_token
def manage_favorite(login_user) -> str:
    news_ids = request.json['news_ids']

    news = db.news.find_one({
        '_id': {
            '$in': news_ids
        }
    })

    if news is None:
        return error(ErrorCause.CONTENT_NOT_EXISTED, 'One of news {} does not exist'.format(news_ids))

    favorite_news = login_user['favorite']

    for news_id in news_ids:
        if request.method == 'PUT':
            if news_id not in favorite_news:
                favorite_news.append(news_id)
        elif request.method == 'DELETE':
            if news_id in favorite_news:
                favorite_news.remove(news_id)

    db.users.update_one({
        '_id': login_user['_id']
    }, {'$set': {
        'favorite': favorite_news
    }})

    return ok()
