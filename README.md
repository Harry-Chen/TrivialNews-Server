# TrivialNews-Server

This is server for TrivialNews, a project of Java course in Tsinghua University, Summer 2018.

The project is licensed under GPLv3.

## Run server

Requirements:

* Python 3.7.0+
* MongoDB 3.0+
* PyPI packages, including:
  * arrow
  * bson
  * flask
  * jieba
  * pymongo
  * pytz
  * requests
  * feedparser

Then run:

`python -m flask run`

You should also run scipts in `preprocessing` to update the database periodically, using a relatively short interval, 5 minutes for example.