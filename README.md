# Dash5S Platform

Веб-платформа для управления проектом внедрения системы 5С.

## Функционал (план)
*   Аутентификация через Active Directory (LDAP)
*   Конструктор чек-листов аудитов 5С
*   Модуль дашборда с визуализацией результатов
*   Система обратной связи
*   Модульная архитектура для расширения

## Технологии
*   Python 3.11+
*   Flask
*   SQLAlchemy (SQLite / PostgreSQL)
*   LDAP3 (интеграция с AD)
*   Chart.js / Plotly (визуализация)

## Разработка

### 1. Клонирование и настройка окружения
```bash
git clone https://github.com/maxfrank76/dash5s-platform.git
cd dash5s-platform
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt

### 2. Запуск тестового LDAP-сервера (опционально)
```bash
docker-compose up -d ldap

### 3. Запуск приложения
```bash
flask run

dash5s_app/
├── app.py                          # Точка входа, инициализация ядра
├── config.py                       # Конфигурация (AD, БД, пути)
├── requirements.txt                # Зависимости
├── core/                           # ЯДРО ПРИЛОЖЕНИЯ
│   ├── __init__.py
│   ├── auth.py                    # Интеграция AD (LDAP), сессии
│   ├── models.py                  # Базовые модели БД (User, Log)
│   ├── admin_views.py             # Панель админа (управление модулями пользователями)
│   ├── navigation.py              # Динамическое меню на основе доступных модулей
│   └── utils.py                   # Логгирование, декораторы доступа
├── modules/                        # МОДУЛИ (PLUGINS)
│   ├── dashboard/                  # МОДУЛЬ 1: Дашборд 5С
│   │   ├── __init__.py
│   │   ├── models.py              # Area, AuditRecord
│   │   ├── views.py               # Роуты дашборда, внесение аудитов
│   │   ├── templates/dashboard/*.html
│   │   └── static/dashboard/*.js/css
│   ├── feedback/                  # МОДУЛЬ 2: Обратная связь
│   │   ├── __init__.py
│   │   ├── models.py              # FeedbackMessage
│   │   └── views.py
│   └── improvements/              # МОДУЛЬ 3: Предложения по улучшению (ЗАГЛУШКА)
│       ├── __init__.py            # Пока содержит только meta-информацию для меню
│       └── placeholder.html       # Страница "Модуль в разработке"
├── migrations/                    # Alembic миграции БД (для каждого модуля своя версия)
├── templates/base.html           # Базовый шаблон с меню и уведомлениями
└── static/global/                # Глобальные CSS, JS (Chart.js, Bootstrap)