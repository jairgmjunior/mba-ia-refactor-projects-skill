from flask import Blueprint, jsonify, request
from controllers import report_controller

report_bp = Blueprint('reports', __name__)

@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return jsonify(report_controller.summary_report()), 200

@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    report = report_controller.user_report(user_id)
    return (jsonify(report), 200) if report else (jsonify({'error': 'Usuário não encontrado'}), 404)

@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(report_controller.list_categories()), 200

@report_bp.route('/categories', methods=['POST'])
def create_category():
    category, error, status = report_controller.create_category(request.get_json())
    return (jsonify({'error': error}), status) if error else (jsonify(category), status)

@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    category, error, status = report_controller.update_category(cat_id, request.get_json() or {})
    return (jsonify({'error': error}), status) if error else (jsonify(category), status)

@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    error, status = report_controller.delete_category(cat_id)
    return (jsonify({'error': error}), status) if error else (jsonify({'message': 'Categoria deletada'}), status)
