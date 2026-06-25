from flask import Blueprint, jsonify, request
from src.controllers import order_controller

order_bp = Blueprint('orders', __name__)

@order_bp.route('/pedidos', methods=['POST'])
def create_order():
    body, status = order_controller.create_order(request.get_json())
    return jsonify(body), status

@order_bp.route('/pedidos', methods=['GET'])
def list_orders():
    body, status = order_controller.list_orders()
    return jsonify(body), status

@order_bp.route('/pedidos/usuario/<int:user_id>', methods=['GET'])
def list_user_orders(user_id):
    body, status = order_controller.list_user_orders(user_id)
    return jsonify(body), status

@order_bp.route('/pedidos/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    body, status = order_controller.update_order_status(order_id, request.get_json())
    return jsonify(body), status

@order_bp.route('/relatorios/vendas', methods=['GET'])
def sales_report():
    body, status = order_controller.sales_report()
    return jsonify(body), status
