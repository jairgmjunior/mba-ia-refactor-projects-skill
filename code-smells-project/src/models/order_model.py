from src.config.database import get_db

def create_order(usuario_id, itens):
    db = get_db()
    total = 0
    products = []
    for item in itens:
        product = db.execute('SELECT * FROM produtos WHERE id = ?', (item['produto_id'],)).fetchone()
        if product is None:
            return {'erro': f"Produto {item['produto_id']} não encontrado"}
        if product['estoque'] < item['quantidade']:
            return {'erro': f"Estoque insuficiente para {product['nome']}"}
        total += product['preco'] * item['quantidade']
        products.append((item, product))
    cursor = db.execute('INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)', (usuario_id, 'pendente', total))
    order_id = cursor.lastrowid
    for item, product in products:
        db.execute('INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)', (order_id, item['produto_id'], item['quantidade'], product['preco']))
        db.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (item['quantidade'], item['produto_id']))
    db.commit()
    return {'pedido_id': order_id, 'total': total}

def order_rows(where='', params=()):
    rows = get_db().execute(f'''
        SELECT p.*, ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        {where}
        ORDER BY p.id
    ''', params).fetchall()
    orders = {}
    for row in rows:
        order = orders.setdefault(row['id'], {'id': row['id'], 'usuario_id': row['usuario_id'], 'status': row['status'], 'total': row['total'], 'criado_em': row['criado_em'], 'itens': []})
        if row['produto_id'] is not None:
            order['itens'].append({'produto_id': row['produto_id'], 'produto_nome': row['produto_nome'] or 'Desconhecido', 'quantidade': row['quantidade'], 'preco_unitario': row['preco_unitario']})
    return list(orders.values())

def list_user_orders(usuario_id):
    return order_rows('WHERE p.usuario_id = ?', (usuario_id,))

def list_orders():
    return order_rows()

def update_order_status(pedido_id, status):
    get_db().execute('UPDATE pedidos SET status = ? WHERE id = ?', (status, pedido_id))
    get_db().commit()

def sales_report():
    db = get_db()
    total_orders = db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]
    revenue = db.execute('SELECT COALESCE(SUM(total), 0) FROM pedidos').fetchone()[0]
    counts = {status: db.execute('SELECT COUNT(*) FROM pedidos WHERE status = ?', (status,)).fetchone()[0] for status in ('pendente', 'aprovado', 'cancelado')}
    discount = 0
    if revenue > 10000:
        discount = revenue * 0.1
    elif revenue > 5000:
        discount = revenue * 0.05
    elif revenue > 1000:
        discount = revenue * 0.02
    return {'total_pedidos': total_orders, 'faturamento_bruto': round(revenue, 2), 'desconto_aplicavel': round(discount, 2), 'faturamento_liquido': round(revenue - discount, 2), 'pedidos_pendentes': counts['pendente'], 'pedidos_aprovados': counts['aprovado'], 'pedidos_cancelados': counts['cancelado'], 'ticket_medio': round(revenue / total_orders, 2) if total_orders else 0}
