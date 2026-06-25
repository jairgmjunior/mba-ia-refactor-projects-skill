from flask import Blueprint, jsonify, request
from controllers import user_controller

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(user_controller.list_users()), 200

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = user_controller.get_user(user_id)
    return (jsonify(user), 200) if user else (jsonify({'error': 'Usuário não encontrado'}), 404)

@user_bp.route('/users', methods=['POST'])
def create_user():
    user, error, status = user_controller.create_user(request.get_json())
    return (jsonify({'error': error}), status) if error else (jsonify(user), status)

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user, error, status = user_controller.update_user(user_id, request.get_json())
    return (jsonify({'error': error}), status) if error else (jsonify(user), status)

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    error, status = user_controller.delete_user(user_id)
    return (jsonify({'error': error}), status) if error else (jsonify({'message': 'Usuário deletado com sucesso'}), status)

@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    tasks = user_controller.user_tasks(user_id)
    return (jsonify(tasks), 200) if tasks is not None else (jsonify({'error': 'Usuário não encontrado'}), 404)

@user_bp.route('/login', methods=['POST'])
def login():
    result, error, status = user_controller.login(request.get_json())
    return (jsonify({'error': error}), status) if error else (jsonify(result), status)
