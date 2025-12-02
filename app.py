from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Импорт моделей после инициализации db
    from core import models
    
    @app.route('/')
    def index():
        return 'Dash5S Platform is starting...'
    
    return app