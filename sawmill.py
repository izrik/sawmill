#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, request, flash
from flask import make_response, Markup, jsonify, json, session
import flask
import argparse
from os import environ
import random
from flask_login import LoginManager, login_user, login_required
from flask_login import logout_user, current_user
from flask_bcrypt import Bcrypt
import git
from database import db
from models.option import Option
from models.user import User
from models.log_entry import LogEntry
from conversions import bool_from_str
import base64
import itertools

try:
    __revision__ = git.Repo('.').git.describe(tags=True, dirty=True,
                                              always=True, abbrev=40)
except git.InvalidGitRepositoryError:
    __revision__ = 'unknown'

DEFAULT_SAWMILL_DEBUG = False
DEFAULT_SAWMILL_PORT = 6892
DEFAULT_SAWMILL_DB_URI = 'sqlite:////tmp/test.db'
DEFAULT_SAWMILL_SECRET_KEY = None


def get_form_or_arg(name, default=None):
    if name in request.form:
        return request.form[name]
    if name in request.args:
        return request.args.get(name)
    return default


def generate_app(db_uri=DEFAULT_SAWMILL_DB_URI,
                 secret_key=DEFAULT_SAWMILL_SECRET_KEY):

    app = Flask(__name__)
    app.secret_key = secret_key

    login_manager = LoginManager()
    login_manager.init_app(app)
    app.login_manager = login_manager
    login_manager.login_view = 'login'

    app.bcrypt = Bcrypt(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.init_app(app)
    app.db = db
    app.app_context().push()

    class Options(object):
        @staticmethod
        def get(key, default_value=None):
            option = Option.query.get(key)
            if option is None:
                return default_value
            return option.value

        @staticmethod
        def get_title():
            return Options.get('title', 'Sawmill')

        @staticmethod
        def get_revision():
            return __revision__

    @app.context_processor
    def setup_options():
        return {'opts': Options}

    @app.route('/')
    @login_required
    def index():
        server = get_form_or_arg('server')
        filter_servers = session.get('filter_servers', [])
        filter_log_names = session.get('filter_log_names', [])
        query = LogEntry.query
        if filter_servers:
            query = query.filter(LogEntry.server.in_(filter_servers))
        if filter_log_names:
            query = query.filter(LogEntry.log_name.in_(filter_log_names))
        query = query.order_by(LogEntry.id)
        pager = query.paginate()
        all_servers = (s[0] for s in db.session.query(LogEntry.server).distinct()
            .order_by(LogEntry.server).all())
        all_log_names = (l[0] for l in db.session.query(LogEntry.log_name)
            .distinct().order_by(LogEntry.log_name).all())
        return render_template('index.t.html', pager=pager,
                               all_servers=all_servers, server=server,
                               filter_servers=filter_servers,
                               all_log_names=all_log_names,
                               izipl=itertools.izip_longest,
                               filter_log_names=filter_log_names)

    @app.route('/apply_filters', methods=["GET", "POST"])
    @login_required
    def apply_filters():
        if request.method == 'GET':
            return redirect(url_for('index'))
        filter_servers = []
        filter_log_names = []
        for k in request.form:
            if k.startswith('server_') and request.form[k]:
                s = k[7:]
                filter_servers.append(s)
            if k.startswith('log_name_') and request.form[k]:
                s = k[9:]
                filter_log_names.append(s)
        session['filter_servers'] = filter_servers
        session['filter_log_names'] = filter_log_names
        return redirect(url_for('index', filter_servers=filter_servers))

    @login_manager.user_loader
    def load_user(userid):
        return User.query.filter_by(email=userid).first()

    @login_manager.request_loader
    def load_user_with_basic_auth(request):
        api_key = request.headers.get('Authorization')
        if api_key:
            api_key = api_key.replace('Basic ', '', 1)
            api_key = base64.b64decode(api_key)
            email, password = api_key.split(':', 1)
            user = User.query.filter_by(email=email).first()

            if (user is None or
                    not app.bcrypt.check_password_hash(
                        user.hashed_password, password)):
                return None

            return user

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            login_failed = request.args.get('login_failed')
            return render_template('login.t.html', login_failed=login_failed)
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        next_url = (request.args.get('next') or request.args.get('next_url') or
                    url_for('index'))

        if (user is None or
                not app.bcrypt.check_password_hash(user.hashed_password,
                                                   password)):
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('login', login_failed=1,
                                    next_url=next_url))

        login_user(user)
        flash('Logged in successfully')
        return redirect(next_url)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/intake', methods=['POST'])
    @login_required
    def intake():
        json = request.get_json()
        timestamp = json['@timestamp']
        server = json['host']
        log_name = json['source']
        message = json['message']
        le = LogEntry(timestamp, server, log_name, message)
        db.session.add(le)
        db.session.commit()
        return ('', 204)

    return app


if __name__ == '__main__':

    SAWMILL_DEBUG = bool_from_str(
        environ.get('SAWMILL_DEBUG', DEFAULT_SAWMILL_DEBUG))
    SAWMILL_PORT = environ.get('SAWMILL_PORT', DEFAULT_SAWMILL_PORT)
    try:
        SAWMILL_PORT = int(SAWMILL_PORT)
    except:
        SAWMILL_PORT = DEFAULT_SAWMILL_PORT
    SAWMILL_DB_URI = environ.get('SAWMILL_DB_URI', DEFAULT_SAWMILL_DB_URI)
    SAWMILL_SECRET_KEY = environ.get('SAWMILL_SECRET_KEY')

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', default=SAWMILL_DEBUG)
    parser.add_argument('--port', action='store', default=SAWMILL_PORT,
                        type=int)
    parser.add_argument('--create-db', action='store_true')
    parser.add_argument('--db-uri', action='store', default=SAWMILL_DB_URI)
    parser.add_argument('--secret-key', action='store',
                        default=SAWMILL_SECRET_KEY)
    parser.add_argument('--create-secret-key', action='store_true')
    parser.add_argument('--hash-password', action='store')

    args = parser.parse_args()

    SAWMILL_DEBUG = args.debug
    SAWMILL_PORT = args.port
    SAWMILL_DB_URI = args.db_uri
    SAWMILL_SECRET_KEY = args.secret_key

    print('__revision__: {}'.format(__revision__))
    print('SAWMILL_DEBUG: {}'.format(SAWMILL_DEBUG))
    print('SAWMILL_PORT: {}'.format(SAWMILL_PORT))
    print('SAWMILL_DB_URI: {}'.format(SAWMILL_DB_URI))

    app = generate_app(db_uri=args.db_uri, secret_key=args.secret_key)

    if args.create_db:
        print('Setting up the database')
        app.db.create_all()
    elif args.create_secret_key:
        digits = '0123456789abcdef'
        key = ''.join((random.choice(digits) for x in xrange(48)))
        print(key)
    elif args.hash_password is not None:
        print(app.bcrypt.generate_password_hash(args.hash_password))
    else:
        app.run(debug=args.debug, port=args.port)
