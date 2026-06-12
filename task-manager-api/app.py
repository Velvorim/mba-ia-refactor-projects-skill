"""
Entry point da aplicação Task Manager API.
Composition root: inicializa Flask, configuração, blueprints e middlewares.
"""
import logging
from datetime import datetime, timezone

from flask import Flask
from flask_cors import CORS

from config import settings
from database import db
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from middlewares.error_handler import register_error_handlers

# Configurar logging estruturado (AP-13 fix: substitui print() statements)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
)

logger = logging.getLogger(__name__)


def create_app():
    """Factory function — cria e configura a aplicação Flask."""
    app = Flask(__name__)

    # Configuração via variáveis de ambiente (AP-02 / AP-11 fix)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    CORS(app)
    db.init_app(app)

    # Blueprints
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    # Middleware de erro centralizado (AP-05 / PT-05 fix)
    register_error_handlers(app)

    # Endpoints utilitários
    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now(timezone.utc))}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    return app


app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # AP-11 fix: debug controlado por variável de ambiente DEBUG
    logger.info("Iniciando Task Manager API em %s:%d (debug=%s)",
                settings.HOST, settings.PORT, settings.DEBUG)
    app.run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
