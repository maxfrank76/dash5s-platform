from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from . import bp
from .models import Area, AuditRecord, AuditResponse
from .forms import AreaForm, AuditForm
from app import db
from datetime import datetime
import calendar

@bp.route('/')
@login_required
def index():
    """Главная страница дашборда."""
    areas = Area.query.filter_by(is_active=True).all()
    
    # Статистика
    total_areas = Area.query.count()
    active_areas = Area.query.filter_by(is_active=True).count()
    this_week = datetime.utcnow().isocalendar()[1]
    audits_this_week = AuditRecord.query.filter_by(week_number=this_week).count()
    
    return render_template('dashboard/index.html',
                         areas=areas,
                         total_areas=total_areas,
                         active_areas=active_areas,
                         audits_this_week=audits_this_week)

@bp.route('/area/<int:area_id>')
@login_required
def area_detail(area_id):
    """Детальная страница участка."""
    area = Area.query.get_or_404(area_id)
    
    # Получаем аудиты за последние 12 недель
    current_week = datetime.utcnow().isocalendar()[1]
    weeks_back = 12
    
    audit_history = []
    for i in range(weeks_back):
        week = current_week - i
        year = datetime.utcnow().year
        
        if week < 1:
            week += 52
            year -= 1
            
        audit = AuditRecord.query.filter_by(
            area_id=area_id,
            week_number=week,
            year=year
        ).first()
        
        audit_history.append({
            'week': week,
            'year': year,
            'audit': audit,
            'score': audit.overall_score if audit else 0
        })
    
    # Получаем последние 5 аудитов
    recent_audits = area.audits.order_by(AuditRecord.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard/area_detail.html',
                         area=area,
                         audit_history=audit_history,
                         recent_audits=recent_audits)

@bp.route('/area/<int:area_id>/audit/new', methods=['GET', 'POST'])
@login_required
def new_audit(area_id):
    """Создание нового аудита для участка."""
    area = Area.query.get_or_404(area_id)
    
    # Проверяем права (только Editor и Admin)
    if current_user.role not in ['Editor', 'Admin']:
        flash('У вас нет прав для проведения аудитов', 'danger')
        return redirect(url_for('dashboard.area_detail', area_id=area_id))
    
    form = AuditForm()
    
    # Устанавливаем значения по умолчанию
    current_date = datetime.utcnow()
    form.week_number.data = current_date.isocalendar()[1]
    form.year.data = current_date.year
    
    if form.validate_on_submit():
        # Проверяем, нет ли уже аудита на эту неделю
        existing = AuditRecord.query.filter_by(
            area_id=area_id,
            week_number=form.week_number.data,
            year=form.year.data
        ).first()
        
        if existing:
            flash('Аудит на эту неделю уже существует', 'warning')
            return redirect(url_for('dashboard.area_detail', area_id=area_id))
        
        # Создаем запись аудита
        audit = AuditRecord(
            area_id=area_id,
            week_number=form.week_number.data,
            year=form.year.data,
            score_1s=form.score_1s.data or 0,
            score_2s=form.score_2s.data or 0,
            score_3s=form.score_3s.data or 0,
            score_4s=form.score_4s.data or 0,
            score_5s=form.score_5s.data or 0,
            overall_score=(
                (form.score_1s.data or 0) +
                (form.score_2s.data or 0) +
                (form.score_3s.data or 0) +
                (form.score_4s.data or 0) +
                (form.score_5s.data or 0)
            ) / 5,
            notes=form.notes.data,
            editor_id=current_user.id
        )
        
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Аудит для участка "{area.name}" успешно создан!', 'success')
        return redirect(url_for('dashboard.area_detail', area_id=area_id))
    
    return render_template('dashboard/audit_form.html',
                         form=form,
                         area=area,
                         title='Новый аудит')

@bp.route('/api/area/<int:area_id>/scores')
@login_required
def area_scores_api(area_id):
    """API для получения баллов участка (для графика)."""
    area = Area.query.get_or_404(area_id)
    
    # Получаем аудиты за последние 8 недель
    audits = area.audits.order_by(AuditRecord.timestamp.desc()).limit(8).all()
    
    data = {
        'weeks': [],
        'scores': [],
        's1': [], 's2': [], 's3': [], 's4': [], 's5': []
    }
    
    for audit in reversed(audits):  # В правильном порядке времени
        data['weeks'].append(f'W{audit.week_number}')
        data['scores'].append(audit.overall_score)
        data['s1'].append(audit.score_1s)
        data['s2'].append(audit.score_2s)
        data['s3'].append(audit.score_3s)
        data['s4'].append(audit.score_4s)
        data['s5'].append(audit.score_5s)
    
    return jsonify(data)

@bp.route('/api/radar/<int:area_id>')
@login_required
def radar_data_api(area_id):
    """API для данных радар-диаграммы."""
    area = Area.query.get_or_404(area_id)
    latest_audit = area.last_audit
    
    if not latest_audit:
        scores = [0, 0, 0, 0, 0]
    else:
        scores = [
            latest_audit.score_1s,
            latest_audit.score_2s,
            latest_audit.score_3s,
            latest_audit.score_4s,
            latest_audit.score_5s
        ]
    
    data = {
        'labels': ['1S', '2S', '3S', '4S', '5S'],
        'datasets': [{
            'label': area.name,
            'data': scores,
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'pointBackgroundColor': 'rgba(54, 162, 235, 1)',
            'pointBorderColor': '#fff',
            'pointHoverBackgroundColor': '#fff',
            'pointHoverBorderColor': 'rgba(54, 162, 235, 1)'
        }]
    }
    
    return jsonify(data)