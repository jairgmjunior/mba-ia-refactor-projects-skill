from src.config.database import get_db

def row_to_product(row):
    return dict(row) if row else None

def list_products():
    return [row_to_product(row) for row in get_db().execute('SELECT * FROM produtos').fetchall()]

def get_product(product_id):
    return row_to_product(get_db().execute('SELECT * FROM produtos WHERE id = ?', (product_id,)).fetchone())

def create_product(nome, descricao, preco, estoque, categoria):
    cursor = get_db().execute('INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)', (nome, descricao, preco, estoque, categoria))
    get_db().commit()
    return cursor.lastrowid

def update_product(product_id, nome, descricao, preco, estoque, categoria):
    get_db().execute('UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?', (nome, descricao, preco, estoque, categoria, product_id))
    get_db().commit()

def delete_product(product_id):
    get_db().execute('DELETE FROM produtos WHERE id = ?', (product_id,))
    get_db().commit()

def search_products(term='', category=None, min_price=None, max_price=None):
    query = 'SELECT * FROM produtos WHERE 1=1'
    params = []
    if term:
        query += ' AND (nome LIKE ? OR descricao LIKE ?)'
        params.extend([f'%{term}%', f'%{term}%'])
    if category:
        query += ' AND categoria = ?'
        params.append(category)
    if min_price is not None:
        query += ' AND preco >= ?'
        params.append(min_price)
    if max_price is not None:
        query += ' AND preco <= ?'
        params.append(max_price)
    return [row_to_product(row) for row in get_db().execute(query, params).fetchall()]
