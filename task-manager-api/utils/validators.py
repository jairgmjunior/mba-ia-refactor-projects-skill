import re
from config.constants import MAX_TITLE_LENGTH, MIN_PASSWORD_LENGTH, MIN_TITLE_LENGTH, VALID_TASK_STATUSES, VALID_USER_ROLES

EMAIL_PATTERN = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'

def validate_task_data(data, partial=False):
    if not data:
        return 'Dados inválidos'
    if not partial or 'title' in data:
        title = data.get('title')
        if not title:
            return 'Título é obrigatório'
        if len(title) < MIN_TITLE_LENGTH:
            return 'Título muito curto'
        if len(title) > MAX_TITLE_LENGTH:
            return 'Título muito longo'
    if 'status' in data and data['status'] not in VALID_TASK_STATUSES:
        return 'Status inválido'
    if 'priority' in data and (data['priority'] < 1 or data['priority'] > 5):
        return 'Prioridade deve ser entre 1 e 5'
    return None

def validate_user_data(data, partial=False):
    if not data:
        return 'Dados inválidos'
    if not partial or 'name' in data:
        if not data.get('name'):
            return 'Nome é obrigatório'
    if not partial or 'email' in data:
        if not data.get('email'):
            return 'Email é obrigatório'
        if not re.match(EMAIL_PATTERN, data['email']):
            return 'Email inválido'
    if not partial or 'password' in data:
        if not data.get('password'):
            return 'Senha é obrigatória'
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return 'Senha deve ter no mínimo 4 caracteres'
    if 'role' in data and data['role'] not in VALID_USER_ROLES:
        return 'Role inválido'
    return None
