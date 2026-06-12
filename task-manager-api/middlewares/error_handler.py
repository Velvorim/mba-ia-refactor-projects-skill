"""
Middleware de tratamento centralizado de erros.
Elimina a duplicação de try/except em cada endpoint (AP-05 / PT-05 fix).
"""
import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Registra handlers de erro globais na aplicação Flask."""

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Método não permitido'}), 405

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        # Dados inválidos, validações de negócio
        return jsonify({'error': str(e)}), 400

    @app.errorhandler(LookupError)
    def handle_lookup_error(e):
        # Entidade não encontrada (404) ou conflito como email duplicado (409)
        msg = str(e)
        if 'já cadastrado' in msg or 'duplicado' in msg:
            return jsonify({'error': msg}), 409
        return jsonify({'error': msg}), 404

    @app.errorhandler(PermissionError)
    def handle_permission_error(e):
        return jsonify({'error': str(e)}), 403

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error("Unhandled exception: %s", e, exc_info=True)
        return jsonify({'error': 'Erro interno do servidor'}), 500
