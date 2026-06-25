from flask import Blueprint, jsonify, request
from src.controllers import user_controller

user_bp = Blueprint('users', __name__)

@user_bp.route('/usuarios', methods=['GET'])
def list_users():
    body, status = user_controller.list_users()
    return jsonify(body), status

@user_bp.route('/usuarios/<int:user_id>', methods=['GET'])
def get_user(user_id):
    body, status = user_controller.get_user(user_id)
    return jsonify(body), status

@user_bp.route('/usuarios', methods=['POST'])
def create_user():
    body, status = user_controller.create_user(request.get_json())
    return jsonify(body), status

@user_bp.route('/login', methods=['POST'])
def login():
    body, status = user_controller.login(request.get_json())
    return jsonify(body), status
