from flask import Flask, jsonify, request, render_template
from database import get_db_connection, init_db
from models import hash_password
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
import sqlite3


app = Flask(__name__)


with app.app_context():
    init_db()

SECRET_KEY = "tajny_klucz_do_jwt"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            return jsonify({'error': 'Token is invalid or expired!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/zadania', methods=['GET'])
def get_zadania():
    conn = get_db_connection()
    zadania = conn.execute('SELECT * FROM zadania').fetchall()
    conn.close()
    return jsonify([dict(row) for row in zadania]), 200

@app.route('/api/zadania/<int:id>', methods=['GET'])
def get_zadanie(id):
    conn = get_db_connection()
    zadanie = conn.execute('SELECT * FROM zadania WHERE id=?', (id,)).fetchone()
    conn.close()
    if zadanie is None:
        return jsonify({'error': 'Zadanie nie znalezione'}), 404
    return jsonify(dict(zadanie)), 200

@app.route('/api/zadania', methods=['POST'])
@token_required
def create_zadanie():
    data = request.get_json()
    required = ['tytul', 'opis', 'deadline', 'priorytet']
    if not all(field in data for field in required):
        return jsonify({'error': 'Brakuje pól'}), 400
    conn = get_db_connection()
    cur = conn.execute(
        'INSERT INTO zadania (tytul, opis, deadline, priorytet) VALUES (?, ?, ?, ?)',
        (data['tytul'], data['opis'], data['deadline'], data['priorytet'])
    )
    conn.commit()
    conn.close()
    return jsonify({'id': cur.lastrowid}), 201

@app.route('/api/zadania/<int:id>', methods=['PUT'])
@token_required
def update_zadanie(id):
    data = request.get_json()
    conn = get_db_connection()
    zadanie = conn.execute('SELECT * FROM zadania WHERE id=?', (id,)).fetchone()
    if zadanie is None:
        return jsonify({'error': 'Zadanie nie znalezione'}), 404
    conn.execute(
        'UPDATE zadania SET tytul=?, opis=?, deadline=?, priorytet=? WHERE id=?',
        (data.get('tytul'), data.get('opis'), data.get('deadline'), data.get('priorytet'), id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Zaktualizowano'}), 200

@app.route('/api/zadania/<int:id>', methods=['DELETE'])
@token_required
def delete_zadanie(id):
    conn = get_db_connection()
    zadanie = conn.execute('SELECT * FROM zadania WHERE id=?', (id,)).fetchone()
    if zadanie is None:
        return jsonify({'error': 'Zadanie nie znalezione'}), 404
    conn.execute('DELETE FROM zadania WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Usunięto zadanie'}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    if not login or not password or len(password) < 6:
        return jsonify({'error': 'Niepoprawny login lub hasło'}), 400

    conn = get_db_connection()
    existing = conn.execute('SELECT * FROM users WHERE login=?', (login,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'error': 'Login już istnieje'}), 400

    hashed = hash_password(password)
    conn.execute('INSERT INTO users (login, hasloHash) VALUES (?, ?)', (login, hashed))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Utworzono konto'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    if not login or not password:
        return jsonify({'error': 'Nie podano loginu lub hasła'}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE login=?', (login,)).fetchone()
    conn.close()

    from models import check_password

    if user is None or not check_password(password, user['hasloHash']):
        return jsonify({'error': 'Nieprawidłowy login lub hasło'}), 401

    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({'token': token})

@app.route('/home')
def home_page():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)


