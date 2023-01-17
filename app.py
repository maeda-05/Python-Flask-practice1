from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import pytz
import os

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
# app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.urandom(24)

# initialize the app with the extension
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

bootstrap = Bootstrap(app)

# SQLalchemyでモデル作成


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False,default=datetime.now(pytz.timezone('Asia/Tokyo')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)


@login_manager.user_loader
def loed_user(user_id):
    user = db.session.execute(
        db.select(User).filter_by(id=user_id)).scalar_one()
    return user


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # SQLalchemyで全てのデータを取得
        posts = Post.query.all()
        # posts = db.session.execute(
        #     db.select(Post).order_by(Post.created_at)).scalars()
        # print('取得データ =>', posts)

        return render_template('index.html', posts=posts)


@app.route('/create', methods=['GET', 'POST'])
# ログインユーザー以外はアクセス不可
@login_required
def create():
    if request.method == 'POST':
        # クライアントサイドから送信データ取得
        title = request.form['title']
        body = request.form['body']

        # SQLalchemyでデータを追加
        post = Post(title=title, body=body)
        db.session.add(post)
        db.session.commit()

        return redirect('/')
    else:
        return render_template('create.html')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
# ログインユーザー以外はアクセス不可
@login_required
def update(id):
    # SQLalchemyで指定IDのデータを取得
    # post = Post.query.get(id)
    post = db.session.execute(db.select(Post).filter_by(id=id)).scalar_one()
    # print('取得データ =>', post)

    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        # データの更新
        post.title = request.form['title']
        post.body = request.form['body']

        db.session.commit()

        return redirect('/')


@app.route('/delete/<int:id>', methods=['GET'])
# ログインユーザー以外はアクセス不可
@login_required
def delete(id):
    # SQLalchemyで指定IDのデータを取得
    # post = Post.query.get(id)
    post = db.session.execute(db.select(Post).filter_by(id=id)).scalar_one()
    # print('取得データ =>', post)

    # SQLalchemyで指定IDのデータを削除
    db.session.delete(post)
    db.session.commit()

    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if password and password:
            user = User(username=username, password=generate_password_hash(
            password, method='sha256'))

            db.session.add(user)
            db.session.commit()
            
            return redirect('/login')
        else:
            return render_template('signup.html')
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username and password:
            try:
                user = db.session.execute(
                db.select(User).filter_by(username=username)).scalar_one()
                if check_password_hash(user.password, password):
                    login_user(user)
                    return redirect('/')
            except NoResultFound:
                print(username, 'のユーザーデータがありません')
                return f'{username}のユーザーデータがありません'
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/logout', methods=['GET'])
# ログインユーザー以外はアクセス不可
@login_required
def logout():
    logout_user()
    return redirect('/login')


@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')
