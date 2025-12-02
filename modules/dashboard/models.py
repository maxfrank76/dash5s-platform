from datetime import datetime
from app import db

class Area(db.Model):
    """Производственный участок (зона внедрения 5С)."""
    __tablename__ = 'areas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 'Склад', 'Сборка', 'НИОКР'
    code = db.Column(db.String(20), unique=True)      # 'SKL', 'SBORKA', 'NIOKR'
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Ответственный
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    audits = db.relationship('AuditRecord', backref='area', lazy='dynamic', cascade='all, delete-orphan')
    manager = db.relationship('User', backref='managed_areas')
    
    def __repr__(self):
        return f'<Area {self.code}: {self.name}>'
    
    @property
    def last_audit(self):
        """Последний аудит участка."""
        return self.audits.order_by(AuditRecord.timestamp.desc()).first()
    
    @property
    def current_score(self):
        """Текущий общий балл (средний за последние 2 недели)."""
        from datetime import timedelta
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        recent_audits = self.audits.filter(AuditRecord.timestamp >= two_weeks_ago).all()
        
        if not recent_audits:
            return 0
        
        total = sum(audit.overall_score for audit in recent_audits)
        return round(total / len(recent_audits), 2)

class AuditRecord(db.Model):
    """Запись аудита 5С."""
    __tablename__ = 'audit_records'
    
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id', ondelete='CASCADE'), nullable=False)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)  # Номер недели в году
    year = db.Column(db.Integer, nullable=False, default=datetime.utcnow().year)
    
    # Баллы по каждому "S" (вычисляются из ответов)
    score_1s = db.Column(db.Float, default=0)
    score_2s = db.Column(db.Float, default=0)
    score_3s = db.Column(db.Float, default=0)
    score_4s = db.Column(db.Float, default=0)
    score_5s = db.Column(db.Float, default=0)
    
    # Общий балл (среднее)
    overall_score = db.Column(db.Float, default=0)
    
    notes = db.Column(db.Text)  # Комментарии аудитора
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    responses = db.relationship('AuditResponse', backref='audit', lazy='dynamic', cascade='all, delete-orphan')
    checklist = db.relationship('Checklist')
    editor = db.relationship('User', backref='conducted_audits')
    
    def __repr__(self):
        return f'<AuditRecord {self.area.code} W{self.week_number} Score: {self.overall_score}>'

class AuditResponse(db.Model):
    """Ответ на конкретный вопрос чек-листа."""
    __tablename__ = 'audit_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audit_records.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('checklist_questions.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # 0, 1, 2
    comment = db.Column(db.Text)
    
    # Связи
    question = db.relationship('ChecklistQuestion')
    
    __table_args__ = (
        db.UniqueConstraint('audit_id', 'question_id', name='unique_audit_question'),
    )
    
    def __repr__(self):
        return f'<AuditResponse Q{self.question_id}: {self.score}>'