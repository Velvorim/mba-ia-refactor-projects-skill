import logging
from flask import jsonify

# PT-05: Error handling centralizado — elimina try/except duplicado em cada rota
logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Registra todos os handlers de erro no app Flask."""

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso nao encontrado", "sucesso": False}), 404

    @app.errorhandler(ValueError)
    def value_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(PermissionError)
    def permission_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 401

    @app.errorhandler(Exception)
    def internal_error(e):
        logger.error("Erro interno nao tratado: %s", e, exc_info=True)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
