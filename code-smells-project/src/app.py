import sys
import os
import logging

# Adiciona src/ ao path para imports relativos funcionarem
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from flask_cors import CORS

from config import settings
from views.routes import bp as api_bp
from middlewares.error_handler import register_error_handlers
from database import get_db

# PT-06: Configuracao de logging substituindo print()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def create_app():
    """Composition root — registra blueprints e middlewares."""
    app = Flask(__name__)

    # PT-01: credenciais via variaveis de ambiente
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    # PT-11: DEBUG via variavel de ambiente
    app.config["DEBUG"] = settings.DEBUG

    CORS(app)

    # Registrar blueprint com todas as rotas
    app.register_blueprint(api_bp)

    # PT-05: Error handling centralizado
    register_error_handlers(app)

    return app


if __name__ == "__main__":
    # Inicializar banco de dados
    get_db()

    logger.info("=" * 50)
    logger.info("SERVIDOR INICIADO")
    logger.info("Rodando em http://localhost:%d", settings.PORT)
    logger.info("=" * 50)

    app = create_app()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
