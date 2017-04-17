from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, Response
from pymongo import MongoClient
from flask_bootstrap import Bootstrap
import flask_admin as admin
from flask_admin import Admin
from flask_mongoengine import MongoEngine
from flask_admin.form import rules
from flask_admin.contrib.mongoengine import ModelView
from flask import Blueprint
from flask_paginate import Pagination
from wtforms import form, fields, validators

import flask_login as login
from flask_login import login_required

app = Flask(__name__)
Bootstrap(app)
client = MongoClient('mongodb://localhost:27017')
mod = Blueprint('main', __name__)


# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'
app.config['MONGODB_SETTINGS'] = {'DB': 'newsItems'}

# Create models
db = MongoEngine()
db.init_app(app)

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


class PostView(ModelView):
    form_subdocument = {
        'static_fields': {
            'form_subdocuments': {
                None: {
                    'form_rules': ('field', 'value', rules.HTML('<hr>')),
                }
            }
        }
    }

class ConfigView(ModelView):
    form_subdocument = {
        'static_fields': {
            'form_subdocuments': {
                None: {
                    'form_rules': ('field', 'value', rules.HTML('<hr>')),
                }
            }
        }
    }

class PageView(ModelView):
    form_subdocument = {
        'static_fields': {
            'form_subdocuments': {
                None: {
                    'form_rules': ('field', 'value', rules.HTML('<hr>')),
                }
            }
        }
    }
'''
 Start login
'''
class User(db.Document):
    login = db.StringField(max_length=80, unique=True)
    email = db.StringField(max_length=120)
    password = db.StringField(max_length=64)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    # Required for administrative interface
    def __unicode__(self):
        return self.login

# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return User.objects(login=self.login.data).first()

class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if User.objects(login=self.login.data):
            raise validators.ValidationError('Duplicate username')

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.setup_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.objects(id=user_id).first()

# Create customized model view class
class MyModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated


# Create customized index view class
class MyAdminIndexView(admin.AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated

'''
 End login
'''

# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


#@app.route("/admin/post/")
#@app.route("/admin/page/", methods = ['GET' , 'POST'])
#@app.route("/admin/config/", methods = ['GET' , 'POST'])


@app.route("/admin/")
@login_required
def admin():
    return redirect("admin/post/")

@mod.route("/")
@app.route("/")
def main():
    db = client.newsItems
    newsItems = []
    configItems = []
    page = request.args.get('page', type=int, default=1)

    skip = (page*5)-5
    results = db.post.find().sort([("datetime", -1)]).skip(skip).limit(5)
    for item in results:
        newsItems.append(item)

    query = db.config.find().limit(1)
    for item in query:
        configItems.append(item)

    pagination = Pagination( page=page, total=results.count(), record_name='records')

    import re
    s = "Example String"
    pagination_links = re.sub("<ul>", "<ul class='pager'>", pagination.links)
    #print(replaced)
    #pagination.links.replace("<ul>", "<ul class='pager'>")
    print(pagination_links)

    return render_template('index.html', newsItems = newsItems, configItems = configItems, pagination = pagination,pagination_links = pagination_links, pages = getPages())

"""
@app.route('/adminindex/')
def index():
    return render_template('adminIndex.html', user=login.current_user)

@app.route('/login/', methods=('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.get_user()
        login.login_user(user)
        return redirect(url_for('index'))

    return render_template('form.html', form=form)


@app.route('/register/', methods=('GET', 'POST'))
def register_view():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User()

        form.populate_obj(user)
        user.save()

        login.login_user(user)
        return redirect(url_for('index'))

    return render_template('form.html', form=form)


@app.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect(url_for('index'))

"""

def getPages():
    db = client.newsItems
    pageItems = []
    query = db.page.find( { 'active': '1' } )
    for page in query:
        pageItems.append(page)

    return(pageItems)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == "__main__":
    # Initialize flask-login
    #init_login()
    #admin = Admin(app, 'Example: Aggregator', template_mode='bootstrap3')
    #admin.add_view(PostView(Post))
    #admin.add_view(ConfigView(Config))
    #admin.add_view(PageView(Page))
    #admin.add_view(MyModelView(User))
    app.run(host='0.0.0.0', debug=True, port=5050)
