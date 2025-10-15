from flask import Flask, jsonify, request, render_template
from database import get_db_connection, init_db

app = Flask(__name__)


with app.app_context():
    init_db()

@app.route('/')
def home():
    return render_template('index.html')

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
def delete_zadanie(id):
    conn = get_db_connection()
    zadanie = conn.execute('SELECT * FROM zadania WHERE id=?', (id,)).fetchone()
    if zadanie is None:
        return jsonify({'error': 'Zadanie nie znalezione'}), 404
    conn.execute('DELETE FROM zadania WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Usunięto zadanie'}), 200

if __name__ == '__main__':
    app.run(debug=True)

