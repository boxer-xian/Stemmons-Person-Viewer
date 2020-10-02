from werkzeug.middleware.dispatcher import DispatcherMiddleware
from index import app as dash_app
from flask import Flask

base_app = Flask(__name__)

@base_app.route('/')
def index():
    return 'Why hello there'

app = DispatcherMiddleware(base_app,{'/test':dash_app.server})