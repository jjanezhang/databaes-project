from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    from .ratings import bp as ratings_bp
    app.register_blueprint(ratings_bp)

    from .order_fulfillment import bp as order_fulfillment_bp
    app.register_blueprint(order_fulfillment_bp)

    from .inventory_and_order_stats import bp as inventory_and_order_stats_bp
    app.register_blueprint(inventory_and_order_stats_bp)

    from .products import bp as products_bp
    app.register_blueprint(products_bp)

    return app
