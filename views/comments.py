from flask import Blueprint
import arrow

from utils.auth_helper import *
from utils.misc import generate_id
from utils.return_result import *

comments = Blueprint('comments', __name__)


@comments.route('/comment', methods=['POST'])
@require_token
def add_comment(login_user) -> str:
    news_id = request.json['news_id']

    news_item = db.news.find_one({
        '_id': news_id
    })

    if news_item is None:
        return error(ErrorCause.CONTENT_NOT_EXISTED, "News {} does not exist".format(news_id))

    new_comment = {
        '_id': generate_id(),
        'user_id': login_user['_id'],
        'news_id': news_id,
        'content': request.json['content'],
        'time': arrow.utcnow().datetime
    }

    db.comments.insert_one(new_comment)

    return ok()


@comments.route('/comment', methods=['DELETE'])
@require_token
def delete_comment(login_user) -> str:
    comment_id = request.json['comment_id']

    comment_item = db.comments.find_one({
        '_id': comment_id
    })

    if comment_item is None:
        return error(ErrorCause.CONTENT_NOT_EXISTED, "Comment {} does not exist".format(comments))

    if comment_item['user_id'] != login_user['_id']:
        return error(ErrorCause.REQUEST_INVALID, "Cannot delete comment that does not belong to you")

    db.comments.delete_one({
        '_id': comment_id
    })

    return ok()
