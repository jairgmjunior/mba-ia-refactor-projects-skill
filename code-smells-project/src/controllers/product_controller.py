from src.models import product_model
from src.utils.validators import validate_product_payload

def list_products():
    return {'dados': product_model.list_products(), 'sucesso': True}, 200

def get_product(product_id):
    product = product_model.get_product(product_id)
    return ({'dados': product, 'sucesso': True}, 200) if product else ({'erro': 'Produto não encontrado', 'sucesso': False}, 404)

def create_product(data):
    error = validate_product_payload(data)
    if error:
        return {'erro': error}, 400
    product_id = product_model.create_product(data['nome'], data.get('descricao', ''), data['preco'], data['estoque'], data.get('categoria', 'geral'))
    return {'dados': {'id': product_id}, 'sucesso': True, 'mensagem': 'Produto criado'}, 201

def update_product(product_id, data):
    if not product_model.get_product(product_id):
        return {'erro': 'Produto não encontrado'}, 404
    error = validate_product_payload(data)
    if error:
        return {'erro': error}, 400
    product_model.update_product(product_id, data['nome'], data.get('descricao', ''), data['preco'], data['estoque'], data.get('categoria', 'geral'))
    return {'sucesso': True, 'mensagem': 'Produto atualizado'}, 200

def delete_product(product_id):
    if not product_model.get_product(product_id):
        return {'erro': 'Produto não encontrado'}, 404
    product_model.delete_product(product_id)
    return {'sucesso': True, 'mensagem': 'Produto deletado'}, 200

def search_products(args):
    min_price = float(args['preco_min']) if args.get('preco_min') else None
    max_price = float(args['preco_max']) if args.get('preco_max') else None
    products = product_model.search_products(args.get('q', ''), args.get('categoria'), min_price, max_price)
    return {'dados': products, 'total': len(products), 'sucesso': True}, 200
