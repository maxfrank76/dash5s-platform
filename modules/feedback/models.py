from datetime import datetime
from app import db

class FeedbackMessage(db.Model):
    """Сообщение обратной связи от пользователей."""
    __tablename__ = 'feedback_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # new, read, in_progress, closed
    admin_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Связи
    user = db.relationship('User', backref='feedback_messages')
    
    def __repr__(self):
        return f'<FeedbackMessage {self.id} from {self.user_id}>'