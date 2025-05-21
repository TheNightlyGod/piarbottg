import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.config.from_object('appconfig.Config')

# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Создание базы данных (если она не существует)
def init_db():
    with sqlite3.connect('data.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            text TEXT,
            time_sec INTEGER,
            image TEXT,
            flask_image TEXT
        )''')
        conn.commit()

# Главная страница
@app.route('/')
def index():
    # Получаем данные из базы
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

# Страница логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Простейшая проверка
        if username == 'luki' and password == '54543757':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Неверные данные', 'danger')

    return render_template('login.html')

# Форма для добавления данных
@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        group_id = request.form['group_id']
        text = request.form['text']
        time_sec = int(request.form['time_sec'])
        image = None
        image_path = None

        # Обработка картинки
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join("static/uploads/", filename)
                file.save(image_path)
                image = "flask/static/uploads/" + filename

        # Сохранение в базу данных
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (group_id, text, time_sec, image, flask_image) VALUES (?, ?, ?, ?, ?)',
                       (group_id, text, time_sec, image, image_path))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('panel.html')

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    flash(f'Запись с ID {post_id} успешно удалена', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)