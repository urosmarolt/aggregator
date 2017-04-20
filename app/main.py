from datetime import datetime
from flask import Flask, render_template, request
from pymongo import MongoClient
from flask_bootstrap import Bootstrap
from flask_mongoengine import MongoEngine
from flask_paginate import Pagination

app = Flask(__name__)
Bootstrap(app)
client = MongoClient('mongodb://localhost:27017')

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'
app.config['MONGODB_SETTINGS'] = {'DB': 'newsItems'}

# Create models
db = MongoEngine()
db.init_app(app)
mongo_db = client.newsItems

# Define mongoengine documents
class Post(db.Document):
    sourceID = db.StringField(max_length=150)
    image = db.StringField(max_length=250)
    title = db.StringField(max_length=150)
    body = db.StringField()
    url = db.StringField(max_length=250)
    sourceUrl = db.StringField(max_length=250)
    sourceTitle = db.StringField(max_length=250)
    lang = db.StringField(max_length=60)
    datetime = db.StringField(max_length=150, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class Config(db.Document):
    appTitle = db.StringField()
    logo =  db.ImageField(thumbnail_size=(250, 250, True))
    aggregatorCategory = db.StringField()
    aggregatorTheme = db.StringField()
    loginUser = db.StringField()
    loginPass = db.StringField()
    metaKeyword = db.StringField()
    metaDescription = db.StringField()
    metaTitle = db.StringField()
    SEOText = db.StringField()
    SEOWidgetTitle = db.StringField()

class Page(db.Document):
    url = db.StringField()
    active = db.BooleanField(default=1)
    title = db.StringField()
    intro =  db.StringField()
    body = db.StringField()
    metaKeyword = db.StringField()
    metaDescription = db.StringField()
    metaTitle = db.StringField()

class Widgets(db.Document):
    widget = db.DictField()

@app.route("/")
def main():
    newsItems = []
    configItems = []
    widgetItems = []
    page = request.args.get('page', type=int, default=1)

    skip = (page*10)-10
    results = mongo_db.post.find().sort([("datetime", -1)]).skip(skip).limit(10)
    for item in results:
        newsItems.append(item)

    query = mongo_db.config.find().limit(1)
    for item in query:
        configItems.append(item)


    query = mongo_db.widget.find()
    for item in query:
        widgetItems.append(item)

    pagination = Pagination( page=page, total=results.count(), record_name='records')
    return render_template('index.html', newsItems = newsItems, configItems = configItems, pagination = pagination,pagination_links = string_replace("<ul>", "<ul class='pager'>", pagination.links), pages = getPages(), widgetItems = widgetItems)

def string_replace(find_str, repl_str, original_text):
    import re
    return re.sub(find_str, repl_str, original_text)

def getPages(url=""):
    pageItems = []
    if url!="":
        query = mongo_db.page.find( { 'active': '1', 'url': url } )
    else:
        query = mongo_db.page.find( { 'active': '1' } )
    for page in query:
        pageItems.append(page)

    return(pageItems)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)