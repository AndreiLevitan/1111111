import sqlite3
from flask import Flask, request, render_template, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')


app = Flask(__name__)
app.secret_key = "super secret key"


class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        print(row)
        return (True, row[0]) if row else (False,)

    def clean(self):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM users")
        cursor.close()
        self.connection.commit()


class NewsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             title VARCHAR(100),
                             content VARCHAR(1000),
                             user_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                          (title, content, user_id) 
                          VALUES (?,?,?)''', (title, content, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", (str(news_id),))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM news WHERE user_id = ?",
                           (str(user_id),))
        else:
            cursor.execute("SELECT * FROM news")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ?''', (str(news_id),))
        cursor.close()
        self.connection.commit()

    def clean(self):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM news")
        cursor.close()
        self.connection.commit()


@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        login = request.form.get('login')
        print(login)
        user_password = request.form.get('password')
        print(user_password)
        user_model = UsersModel(database.get_connection())
        print(login, user_password)
        exists = user_model.exists(login, user_password)
        print(exists)
        if exists[0]:
            session['username'] = login
            session['user_id'] = exists[1]
        return redirect('/feed')


@app.route('/feed', methods=['POST', 'GET'])
def feed():
    if 'username' not in session:
        print('User not in session')
        return redirect('/login')
    if request.method == 'GET':
        cur_user_news = news.get_all(user_id=session['user_id'])
        return render_template('feed.html', news=cur_user_news)
    elif request.method == 'POST':
        pass


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/delete_news/<news_id>')
def delete_news(news_id):
    if 'username' not in session:
        print('User not in session')
        return redirect('/login')
    print(session['user_id'])
    print(news.get(news_id=news_id)[3])
    if session['user_id'] == news.get(news_id=news_id)[3]:
        news.delete(news_id=news_id)
        print('Удаление...')
        return render_template('delete_news.html', user=session['username'])
    return redirect('/feed')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        nm = NewsModel(database.get_connection())
        nm.insert(title, content, session['user_id'])
        return redirect("/feed")
    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'])


if __name__ == '__main__':
    database = DB()
    users = UsersModel(database.get_connection())
    print(users.get_all())
    print(users.exists('Andrey', '12345678'))
    # users.init_table()
    # users.clean()
    # users.insert('Andrey', '12345678')
    # users.insert('ProGamer', '13371212')
    # users.insert('Nastenka', 'qwerty')
    print(users.get_all())

    news = NewsModel(database.get_connection())
    # news.init_table()
    # news.clean()
    # news.insert('1', 'Новость для удаления', '85')
    app.run(port=8000, host='127.0.0.1')

