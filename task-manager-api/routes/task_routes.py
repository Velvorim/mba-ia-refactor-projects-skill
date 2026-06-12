"""
Task Routes — camada de transporte HTTP.
Responsabilidade: extrair parâmetros da request, chamar o controller,
retornar a response. Sem lógica de negócio inline.
"""
from flask import Blueprint, request, jsonify
from controllers import task_controller

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(task_controller.listar_tasks()), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    data = task_controller.buscar_task(task_id)
    return jsonify(data), 200


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    return jsonify(task_controller.criar_task(request.get_json())), 201


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    return jsonify(task_controller.atualizar_task(task_id, request.get_json())), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    return jsonify(task_controller.deletar_task(task_id)), 200


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    result = task_controller.pesquisar_tasks(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )
    return jsonify(result), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(task_controller.estatisticas_tasks()), 200
