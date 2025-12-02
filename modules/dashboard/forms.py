from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange

class AreaForm(FlaskForm):
    """Форма создания/редактирования участка."""
    name = StringField('Название участка', validators=[DataRequired(), Length(max=100)])
    code = StringField('Код участка', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Описание')
    manager_id = SelectField('Ответственный', coerce=int)

class AuditForm(FlaskForm):
    """Форма проведения аудита."""
    week_number = IntegerField('Номер недели', validators=[DataRequired(), NumberRange(min=1, max=53)])
    year = IntegerField('Год', validators=[DataRequired(), NumberRange(min=2023, max=2030)])
    
    # Поля для быстрого ввода баллов (альтернатива ответам на вопросы)
    score_1s = FloatField('1S - Сортировка', validators=[NumberRange(min=0, max=2)])
    score_2s = FloatField('2S - Соблюдение порядка', validators=[NumberRange(min=0, max=2)])
    score_3s = FloatField('3S - Чистота', validators=[NumberRange(min=0, max=2)])
    score_4s = FloatField('4S - Стандартизация', validators=[NumberRange(min=0, max=2)])
    score_5s = FloatField('5S - Совершенствование', validators=[NumberRange(min=0, max=2)])
    
    notes = TextAreaField('Комментарии и замечания')