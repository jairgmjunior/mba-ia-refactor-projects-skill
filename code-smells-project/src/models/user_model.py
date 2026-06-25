from src.config.database import get_db

def public_user(row, include_password=False):
    if not row:
        return None
    data = dict(row)
    if not include_password:
        data.pop('senha', None)
    return data

def list_users():
    return [public_user(row) for row in get_db().execute('SELECT * FROM usuarios').fetchall()]

def get_user(user_id):
    return public_user(get_db().execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone())

def authenticate(email, senha):
    row = get_db().execute('SELECT id, nome, email, tipo FROM usuarios WHERE email = ? AND senha = ?', (email, senha)).fetchone()
    return dict(row) if row else None

def create_user(nome, email, senha, tipo='cliente'):
    cursor = get_db().execute('INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)', (nome, email, senha, tipo))
    get_db().commit()
    return cursor.lastrowid
