from flask import Blueprint

from utils.auth_helper import *
from utils.return_result import *

channel = Blueprint('channel', __name__)


@channel.route('/channel/list', methods=['GET'])
def get_channel_list() -> str:
    all_categories = list(db.categories.find({}))

    for category in all_categories:
        del category['link']
        for _channel in category['channels']:
            del _channel['feed_link']

    return ok(all_categories)


@channel.route('/channel/subscribe', methods=['PUT', 'DELETE'])
@require_token
def manage_subscribe(login_user) -> str:
    channel_ids = request.json['channel_ids']

    channel_check = db.channels.find_one({
        '_id': {
            '$in': channel_ids
        }
    })

    if channel_check is None:
        return error(ErrorCause.CONTENT_NOT_EXISTED, 'One of channel {} does not exist'.format(channel_ids))

    subscribed_channels = login_user['subscription']

    for channel_id in channel_ids:
        if request.method == 'PUT':
            if channel_id not in subscribed_channels:
                subscribed_channels.append(channel_id)
        elif request.method == 'DELETE':
            if channel_id in subscribed_channels:
                subscribed_channels.remove(channel_id)

    db.users.update_one({
        '_id': login_user['_id']
    }, {'$set': {
        'subscription': subscribed_channels
    }})

    return ok()
