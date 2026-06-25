from flask import Flask, jsonify, request
from flask_cors import CORS
from src.config.database import database, get_db
from src.config.settings import Settings
from src.middleware.error_handler import register_error_handlers
from src.routes.order_routes import order_bp
from src.routes.product_routes import product_bp
from src.routes.user_routes import user_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Settings.SECRET_KEY
    app.config['DEBUG'] = Settings.DEBUG
    CORS(app)
    register_error_handlers(app)
    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(order_bp)

    @app.route('/')
    def index():
        return jsonify({'mensagem': 'Bem-vindo à API da Loja', 'versao': '1.0.0', 'endpoints': {'produtos': '/produtos', 'usuarios': '/usuarios', 'pedidos': '/pedidos', 'login': '/login', 'relatorios': '/relatorios/vendas', 'health': '/health'}})

    @app.route('/health')
    def health():
        db = get_db()
        return jsonify({'status': 'ok', 'database': 'connected', 'counts': {'produtos': db.execute('SELECT COUNT(*) FROM produtos').fetchone()[0], 'usuarios': db.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0], 'pedidos': db.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0]}, 'versao': '1.0.0', 'ambiente': 'producao'})

    @app.route('/admin/reset-db', methods=['POST'])
    def reset_database():
        if not Settings.ADMIN_TOKEN or request.headers.get('X-Admin-Token') != Settings.ADMIN_TOKEN:
            return jsonify({'erro': 'Acesso negado'}), 403
        database.reset()
        return jsonify({'mensagem': 'Banco de dados resetado', 'sucesso': True}), 200

    return app
