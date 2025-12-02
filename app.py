import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Эндпоинт для страницы входа
migrate = Migrate()

def create_app(config_class=Config):
    """Фабрика приложения Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Импорт моделей ДО создания контекста приложения
    from core import models as core_models
    from modules.dashboard import models as dashboard_models
    
    # Регистрация Blueprint из ядра
    from core.views import bp as core_bp
    from core.views import auth_bp, admin_bp
    
    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # Регистрация модуля Dashboard
    try:
        from modules.dashboard import bp as dashboard_bp
        app.register_blueprint(dashboard_bp)
        app.logger.info('Dashboard module registered successfully')
    except ImportError as e:
        app.logger.warning(f'Dashboard module not registered: {e}')
    
    # Регистрация модуля Feedback
    try:
        from modules.feedback import bp as feedback_bp
        app.register_blueprint(feedback_bp)
        app.logger.info('Feedback module registered successfully')
    except ImportError as e:
        app.logger.warning(f'Feedback module not registered: {e}')
    
    # Обработчики ошибок
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Контекстный процессор для передачи данных во все шаблоны
    @app.context_processor
    def inject_global_vars():
        from core.models import CoreModule
        from flask_login import current_user
        
        active_modules = []
        try:
            active_modules = CoreModule.query.filter_by(is_active=True).order_by(CoreModule.menu_order).all()
        except Exception as e:
            app.logger.warning(f'Could not load modules: {e}')
        
        return dict(
            active_modules=active_modules,
            current_user=current_user
        )
    
    # Создание таблиц и начальных данных при первом запуске
    with app.app_context():
        create_tables(app)
        create_initial_data(app)
    
    return app

def create_tables(app):
    """Создание таблиц в базе данных."""
    try:
        db.create_all()
        app.logger.info('Database tables created/verified')
    except Exception as e:
        app.logger.error(f'Error creating tables: {e}')

def create_initial_data(app):
    """Создание начальных данных при первом запуске."""
    from core.models import CoreModule
    from modules.dashboard.models import Area
    
    # Создаем базовые модули, если их нет
    if CoreModule.query.count() == 0:
        modules = [
            CoreModule(
                name='dashboard', 
                display_name='Дашборд 5С', 
                menu_order=100, 
                is_active=True,
                version='1.0.0'
            ),
            CoreModule(
                name='feedback', 
                display_name='Обратная связь', 
                menu_order=200, 
                is_active=True,
                version='1.0.0'
            ),
            CoreModule(
                name='admin', 
                display_name='Администрирование', 
                menu_order=900, 
                is_active=True,
                version='1.0.0'
            ),
        ]
        
        for module in modules:
            db.session.add(module)
        
        db.session.commit()
        app.logger.info('Core modules created')
    
    # Создаем тестовые участки, если их нет
    if Area.query.count() == 0:
        areas = [
            Area(
                name='Склад', 
                code='SKL', 
                description='Основной склад материалов и комплектующих',
                is_active=True
            ),
            Area(
                name='Сборочный цех', 
                code='SBORKA', 
                description='Сборка электротехнических шкафов',
                is_active=True
            ),
            Area(
                name='НИОКР и станочный парк', 
                code='NIOKR', 
                description='Опытное производство и станочный парк',
                is_active=True
            ),
        ]
        
        for area in areas:
            db.session.add(area)
        
        db.session.commit()
        app.logger.info('Sample areas created')

# Для запуска приложения напрямую
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)