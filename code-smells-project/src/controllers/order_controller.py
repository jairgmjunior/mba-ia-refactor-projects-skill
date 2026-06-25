from src.models import order_model
from src.utils.validators import validate_order_status

def create_order(data):
    if not data:
        return {'erro': 'Dados inválidos'}, 400
    usuario_id = data.get('usuario_id')
    itens = data.get('itens', [])
    if not usuario_id:
        return {'erro': 'Usuario ID é obrigatório'}, 400
    if not itens:
        return {'erro': 'Pedido deve ter pelo menos 1 item'}, 400
    result = order_model.create_order(usuario_id, itens)
    if 'erro' in result:
        return {'erro': result['erro'], 'sucesso': False}, 400
    return {'dados': result, 'sucesso': True, 'mensagem': 'Pedido criado com sucesso'}, 201

def list_user_orders(usuario_id):
    return {'dados': order_model.list_user_orders(usuario_id), 'sucesso': True}, 200

def list_orders():
    return {'dados': order_model.list_orders(), 'sucesso': True}, 200

def update_order_status(pedido_id, data):
    status = data.get('status', '') if data else ''
    if not validate_order_status(status):
        return {'erro': 'Status inválido'}, 400
    order_model.update_order_status(pedido_id, status)
    return {'sucesso': True, 'mensagem': 'Status atualizado'}, 200

def sales_report():
    return {'dados': order_model.sales_report(), 'sucesso': True}, 200
