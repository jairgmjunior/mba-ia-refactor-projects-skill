import os

class Settings:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'loja.db')
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', '5000'))
