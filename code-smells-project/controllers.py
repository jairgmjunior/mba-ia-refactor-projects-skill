from flask import jsonify, request
from src.controllers import order_controller, product_controller, user_controller
from src.config.database import get_db

def _response(result):
    body, status = result
    return jsonify(body), status

def listar_produtos(): return _response(product_controller.list_products())
def buscar_produto(id): return _response(product_controller.get_product(id))
def criar_produto(): return _response(product_controller.create_product(request.get_json()))
def atualizar_produto(id): return _response(product_controller.update_product(id, request.get_json()))
def deletar_produto(id): return _response(product_controller.delete_product(id))
def buscar_produtos(): return _response(product_controller.search_products(request.args))
def listar_usuarios(): return _response(user_controller.list_users())
def buscar_usuario(id): return _response(user_controller.get_user(id))
def criar_usuario(): return _response(user_controller.create_user(request.get_json()))
def login(): return _response(user_controller.login(request.get_json()))
def criar_pedido(): return _response(order_controller.create_order(request.get_json()))
def listar_pedidos_usuario(usuario_id): return _response(order_controller.list_user_orders(usuario_id))
def listar_todos_pedidos(): return _response(order_controller.list_orders())
def atualizar_status_pedido(pedido_id): return _response(order_controller.update_order_status(pedido_id, request.get_json()))
def relatorio_vendas(): return _response(order_controller.sales_report())
def health_check():
    db = get_db()
    return jsonify({'status': 'ok', 'database': 'connected', 'counts': {'produtos': db.execute('SELECT COUNT(*) FROM produtos').fetchone()[0], 'usuarios': db.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0], 'pedidos': db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]}}), 200
