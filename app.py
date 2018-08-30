from flask import Flask
from utils.return_result import *
from utils.error_cause import ErrorCause
from .views.user import user
from .views.channel import channel
from .views.news import news
from .views.comments import comments

app = Flask(__name__)
app.register_blueprint(user)
app.register_blueprint(channel)
app.register_blueprint(news)
app.register_blueprint(comments)


@app.errorhandler(Exception)
def error_handler(e: Exception) -> str:
    return error(ErrorCause.REQUEST_INVALID, type(e).__name__ + ": " + str(e))


@app.route('/')
def hello_world() -> str:
    return ok("Hello World!")


if __name__ == '__main__':
    app.run()
