from flask import Blueprint, jsonify, request
from src.controllers import product_controller

product_bp = Blueprint('products', __name__)

@product_bp.route('/produtos', methods=['GET'])
def list_products():
    body, status = product_controller.list_products()
    return jsonify(body), status

@product_bp.route('/produtos/busca', methods=['GET'])
def search_products():
    body, status = product_controller.search_products(request.args)
    return jsonify(body), status

@product_bp.route('/produtos/<int:product_id>', methods=['GET'])
def get_product(product_id):
    body, status = product_controller.get_product(product_id)
    return jsonify(body), status

@product_bp.route('/produtos', methods=['POST'])
def create_product():
    body, status = product_controller.create_product(request.get_json())
    return jsonify(body), status

@product_bp.route('/produtos/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    body, status = product_controller.update_product(product_id, request.get_json())
    return jsonify(body), status

@product_bp.route('/produtos/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    body, status = product_controller.delete_product(product_id)
    return jsonify(body), status
