"""
Configuração centralizada da aplicação.
Todos os valores são lidos de variáveis de ambiente com fallback para desenvolvimento.
NÃO colocar valores reais de produção aqui — use variáveis de ambiente ou arquivo .env.
"""
import os
from dotenv import load_dotenv

# Carrega .env se existir (desenvolvimento local)
load_dotenv()

# Banco de dados
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL',
    'sqlite:///tasks.db'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Segurança
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-in-prod')

# Servidor
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '5000'))

# Email SMTP
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
