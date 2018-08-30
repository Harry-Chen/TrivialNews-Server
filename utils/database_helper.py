from pymongo import MongoClient
from bson.codec_options import CodecOptions
import pytz
import config


class DataBaseHelper:

    client = MongoClient(config.MONGO_SERVER, config.MONGO_PORT)
    db = client['trivial_news']

    tz = pytz.timezone('Asia/Shanghai')
    tz_option = CodecOptions(tz_aware=True, tzinfo=tz)

    users = db['Users']
    categories = db['Categories']
    channels = db['Channels']
    comments = db['Comments'].with_options(codec_options=tz_option)
    news = db['News'].with_options(codec_options=tz_option)
    statistics = db['Statistics'].with_options(codec_options=tz_option)


db = DataBaseHelper()
