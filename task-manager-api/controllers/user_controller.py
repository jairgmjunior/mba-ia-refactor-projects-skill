from database import db
from models.task import Task
from models.user import User
from utils.validators import validate_user_data
from controllers.task_controller import serialize_task

def list_users():
    return [user.to_dict() for user in User.query.all()]

def get_user(user_id):
    user = db.session.get(User, user_id)
    return user.to_dict() if user else None

def create_user(data):
    error = validate_user_data(data)
    if error:
        return None, error, 400
    if User.query.filter_by(email=data['email']).first():
        return None, 'Email já cadastrado', 409
    user = User(name=data['name'], email=data['email'], role=data.get('role', 'user'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), None, 201

def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        return None, 'Usuário não encontrado', 404
    error = validate_user_data(data, partial=True)
    if error:
        return None, error, 400
    for field in ('name', 'email', 'role', 'active'):
        if field in data:
            setattr(user, field, data[field])
    if 'password' in data:
        user.set_password(data['password'])
    db.session.commit()
    return user.to_dict(), None, 200

def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return 'Usuário não encontrado', 404
    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return None, 200

def user_tasks(user_id):
    if not db.session.get(User, user_id):
        return None
    return [serialize_task(task) for task in Task.query.filter_by(user_id=user_id).all()]

def login(data):
    if not data or not data.get('email') or not data.get('password'):
        return None, 'Email e senha são obrigatórios', 400
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return None, 'Credenciais inválidas', 401
    if not user.active:
        return None, 'Usuário inativo', 403
    return {'message': 'Login realizado com sucesso', 'user': user.to_dict(), 'token': f'fake-jwt-token-{user.id}'}, None, 200
