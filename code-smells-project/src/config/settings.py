import os

# PT-01: Todas as credenciais e configuracoes via variaveis de ambiente
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-prod")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
