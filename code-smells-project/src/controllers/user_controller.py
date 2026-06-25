from src.models import user_model

def list_users():
    return {'dados': user_model.list_users(), 'sucesso': True}, 200

def get_user(user_id):
    user = user_model.get_user(user_id)
    return ({'dados': user, 'sucesso': True}, 200) if user else ({'erro': 'Usuário não encontrado'}, 404)

def create_user(data):
    if not data:
        return {'erro': 'Dados inválidos'}, 400
    nome = data.get('nome', '')
    email = data.get('email', '')
    senha = data.get('senha', '')
    if not nome or not email or not senha:
        return {'erro': 'Nome, email e senha são obrigatórios'}, 400
    return {'dados': {'id': user_model.create_user(nome, email, senha)}, 'sucesso': True}, 201

def login(data):
    email = data.get('email', '') if data else ''
    senha = data.get('senha', '') if data else ''
    if not email or not senha:
        return {'erro': 'Email e senha são obrigatórios'}, 400
    user = user_model.authenticate(email, senha)
    return ({'dados': user, 'sucesso': True, 'mensagem': 'Login OK'}, 200) if user else ({'erro': 'Email ou senha inválidos', 'sucesso': False}, 401)
