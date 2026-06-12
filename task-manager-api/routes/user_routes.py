"""
User Routes — camada de transporte HTTP.
Responsabilidade: extrair parâmetros da request, chamar o controller,
retornar a response. Sem lógica de negócio inline.
"""
from flask import Blueprint, request, jsonify
from controllers import user_controller

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(user_controller.listar_usuarios()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(user_controller.buscar_usuario(user_id)), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    return jsonify(user_controller.criar_usuario(request.get_json())), 201


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return jsonify(user_controller.atualizar_usuario(user_id, request.get_json())), 200


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return jsonify(user_controller.deletar_usuario(user_id)), 200


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    return jsonify(user_controller.tarefas_do_usuario(user_id)), 200


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    result = user_controller.login(
        email=data.get('email', ''),
        password=data.get('password', ''),
    )
    return jsonify(result), 200
