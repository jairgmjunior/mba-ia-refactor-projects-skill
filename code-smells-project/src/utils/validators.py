from src.utils.constants import MAX_PRODUCT_NAME_LENGTH, MIN_PRODUCT_NAME_LENGTH, VALID_CATEGORIES, VALID_ORDER_STATUSES

def validate_product_payload(data):
    if not data:
        return 'Dados inválidos'
    required = {'nome': 'Nome', 'preco': 'Preço', 'estoque': 'Estoque'}
    for field, label in required.items():
        if field not in data:
            return f'{label} é obrigatório'
    if data['preco'] < 0:
        return 'Preço não pode ser negativo'
    if data['estoque'] < 0:
        return 'Estoque não pode ser negativo'
    if len(data['nome']) < MIN_PRODUCT_NAME_LENGTH:
        return 'Nome muito curto'
    if len(data['nome']) > MAX_PRODUCT_NAME_LENGTH:
        return 'Nome muito longo'
    if data.get('categoria', 'geral') not in VALID_CATEGORIES:
        return f'Categoria inválida. Válidas: {VALID_CATEGORIES}'
    return None

def validate_order_status(status):
    return status in VALID_ORDER_STATUSES
