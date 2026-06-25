from flask import Blueprint, jsonify, request
from controllers import task_controller

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(task_controller.list_tasks()), 200

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = task_controller.get_task(task_id)
    return (jsonify(task), 200) if task else (jsonify({'error': 'Task não encontrada'}), 404)

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    task, error, status = task_controller.create_task(request.get_json())
    return (jsonify({'error': error}), status) if error else (jsonify(task), status)

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task, error, status = task_controller.update_task(task_id, request.get_json())
    return (jsonify({'error': error}), status) if error else (jsonify(task), status)

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    error, status = task_controller.delete_task(task_id)
    return (jsonify({'error': error}), status) if error else (jsonify({'message': 'Task deletada com sucesso'}), status)

@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    return jsonify(task_controller.search_tasks(request.args)), 200
