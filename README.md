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