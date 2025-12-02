from flask import Blueprint, render_template, redirect, url_for, flash, request, g, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .auth import LDAPAuth
from .models import User, VisitLog, CoreModule, db
from datetime import datetime

# Обработка импорта url_parse для совместимости с разными версиями Werkzeug
try:
    # Для Werkzeug < 2.0
    from werkzeug.urls import url_parse
except ImportError:
    # Для Werkzeug >= 2.0
    from urllib.parse import urlparse as url_parse

from .auth import LDAPAuth
from .models import User, VisitLog, CoreModule, db
from datetime import datetime

bp = Blueprint('core', __name__)


@bp.before_app_request
def before_request():
    """Выполняется перед каждым запросом."""
    # Сохранение активных модулей в g для использования в шаблонах
    g.active_modules = CoreModule.query.filter_by(is_active=True).order_by(CoreModule.menu_order).all()
    
    # Логирование действий аутентифицированных пользователей
    if current_user.is_authenticated:
        log = VisitLog(
            user_id=current_user.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            endpoint=request.endpoint,
            action=request.method
        )
        db.session.add(log)
        db.session.commit()


@bp.route('/')
def index():
    """Главная страница."""
    if current_user.is_authenticated:
        # Перенаправление на дашборд для авторизованных пользователей
        return redirect(url_for('dashboard.index'))
    return render_template('home.html')  # Используем новую страницу


# Создадим отдельный Blueprint для аутентификации
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа в систему."""
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Аутентификация через LDAP
        user = LDAPAuth.authenticate(username, password)
        
        if user:
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Добро пожаловать, {user.display_name}!', 'success')
            
            # Перенаправление на следующую страницу или главную
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard.index')
            return redirect(next_page)
        else:
            flash('Неверный логин или пароль', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из системы."""
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('core.index'))


# Blueprint для административной панели
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
def index():
    """Панель администратора."""
    if current_user.role != 'Admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('core.index'))
    
    # Статистика
    user_count = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    recent_logs = VisitLog.query.order_by(VisitLog.timestamp.desc()).limit(10).all()
    
    return render_template('admin/index.html',
                         user_count=user_count,
                         active_users=active_users,
                         recent_logs=recent_logs)


@admin_bp.route('/modules')
@login_required
def module_management():
    """Управление модулями."""
    if current_user.role != 'Admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('core.index'))
    
    modules = CoreModule.query.order_by(CoreModule.menu_order).all()
    return render_template('admin/modules.html', modules=modules)