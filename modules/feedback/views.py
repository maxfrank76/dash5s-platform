from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from . import bp
from .models import FeedbackMessage
from app import db

@bp.route('/')
@login_required
def index():
    """Страница обратной связи."""
    # Получаем сообщения пользователя
    messages = FeedbackMessage.query.filter_by(
        user_id=current_user.id
    ).order_by(FeedbackMessage.created_at.desc()).all()
    
    return render_template('feedback/index.html', messages=messages)

@bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Отправка сообщения обратной связи."""
    message_text = request.form.get('message', '').strip()
    
    if not message_text:
        flash('Сообщение не может быть пустым', 'warning')
        return redirect(url_for('feedback.index'))
    
    if len(message_text) < 10:
        flash('Сообщение слишком короткое (минимум 10 символов)', 'warning')
        return redirect(url_for('feedback.index'))
    
    # Создаем сообщение
    message = FeedbackMessage(
        user_id=current_user.id,
        message=message_text,
        status='new'
    )
    
    db.session.add(message)
    db.session.commit()
    
    flash('Сообщение отправлено администратору', 'success')
    return redirect(url_for('feedback.index'))

@bp.route('/api/messages')
@login_required
def get_messages_api():
    """API для получения сообщений (JSON)."""
    messages = FeedbackMessage.query.filter_by(
        user_id=current_user.id
    ).order_by(FeedbackMessage.created_at.desc()).all()
    
    data = []
    for msg in messages:
        data.append({
            'id': msg.id,
            'message': msg.message,
            'status': msg.status,
            'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M'),
            'admin_comment': msg.admin_comment
        })
    
    return jsonify(data)