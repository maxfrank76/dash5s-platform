from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    """Модель пользователя (кэшируется из AD)."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # user@domain.ru
    display_name = db.Column(db.String(120))  # ФИО из AD
    email = db.Column(db.String(120))
    department = db.Column(db.String(120))    # Отдел из AD
    role = db.Column(db.String(20), default='Viewer')  # 'Viewer', 'Editor', 'Admin'
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
   # audit_records = db.relationship('AuditRecord', backref='editor', lazy='dynamic')
    feedback_messages = db.relationship('FeedbackMessage', backref='author', lazy='dynamic')
    visit_logs = db.relationship('VisitLog', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class VisitLog(db.Model):
    """Лог посещений и действий пользователей."""
    __tablename__ = 'visit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    endpoint = db.Column(db.String(200))      # Например, 'dashboard.index'
    action = db.Column(db.String(100))        # Например, 'login', 'view_page', 'submit_audit'
    details = db.Column(db.Text)              # Дополнительная информация (JSON)
    
    def __repr__(self):
        return f'<VisitLog {self.user_id} - {self.action} at {self.timestamp}>'

class CoreModule(db.Model):
    """Реестр активных модулей системы."""
    __tablename__ = 'core_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 'dashboard', 'feedback'
    display_name = db.Column(db.String(100))                      # 'Дашборд 5С'
    is_active = db.Column(db.Boolean, default=True)
    menu_order = db.Column(db.Integer, default=999)
    version = db.Column(db.String(20), default='1.0.0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CoreModule {self.name} (active: {self.is_active})>'

# Модели для конструктора чек-листов
class Checklist(db.Model):
    """Шаблон чек-листа (например, '5С для сборочного цеха')."""
    __tablename__ = 'checklists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    module = db.Column(db.String(50), default='dashboard')  # Какой модуль использует
    version = db.Column(db.String(20), default='1.0')
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Связи
    sections = db.relationship('ChecklistSection', backref='checklist', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('ChecklistAssignment', backref='checklist', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Checklist {self.name} v{self.version}>'

class ChecklistSection(db.Model):
    """Раздел/подраздел чек-листа."""
    __tablename__ = 'checklist_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists.id', ondelete='CASCADE'), nullable=False)
    parent_section_id = db.Column(db.Integer, db.ForeignKey('checklist_sections.id', ondelete='CASCADE'))
    order_num = db.Column(db.Integer, nullable=False, default=0)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    # Связи
    questions = db.relationship('ChecklistQuestion', backref='section', lazy='dynamic', cascade='all, delete-orphan')
    children = db.relationship('ChecklistSection', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def __repr__(self):
        return f'<ChecklistSection {self.title}>'

class ChecklistQuestion(db.Model):
    """Вопрос в чек-листе."""
    __tablename__ = 'checklist_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('checklist_sections.id', ondelete='CASCADE'), nullable=False)
    order_num = db.Column(db.Integer, nullable=False, default=0)
    question_text = db.Column(db.Text, nullable=False)
    help_text = db.Column(db.Text)                      # Подсказка для аудитора
    weight = db.Column(db.Float, default=1.0)          # Вес вопроса (для расчета)
    is_required = db.Column(db.Boolean, default=True)
    max_score = db.Column(db.Integer, default=2)       # Максимальный балл (0-1-2)
    
    def __repr__(self):
        return f'<ChecklistQuestion {self.id}: {self.question_text[:50]}...>'

class ChecklistAssignment(db.Model):
    """Привязка чек-листа к объекту (участку, типу рабочего места)."""
    __tablename__ = 'checklist_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists.id', ondelete='CASCADE'), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # 'area', 'workplace_type'
    entity_id = db.Column(db.Integer, nullable=False)       # ID участка или типа
    
    # Ограничение: одна активная привязка на сущность
    __table_args__ = (
        db.UniqueConstraint('entity_type', 'entity_id', name='unique_assignment'),
    )
    
    def __repr__(self):
        return f'<ChecklistAssignment {self.checklist_id} -> {self.entity_type}:{self.entity_id}>'

# Функция для загрузки пользователя (требуется Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))