import logging
from flask import current_app, flash
from flask_login import login_user
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException
from .models import User, db

logger = logging.getLogger(__name__)

class LDAPAuth:
    """Класс для работы с аутентификацией через LDAP/AD."""
    
    @staticmethod
    def authenticate(username, password):
        """Аутентификация пользователя через LDAP."""
        if not username or not password:
            return None
            
        try:
            # Подключение к LDAP-серверу
            server = Server(
                current_app.config['LDAP_SERVER'],
                port=current_app.config['LDAP_PORT'],
                use_ssl=current_app.config['LDAP_USE_SSL'],
                get_info=ALL
            )
            
            # Поиск DN пользователя
            search_filter = f"({current_app.config['LDAP_USER_LOGIN_ATTR']}={username})"
            
            with Connection(server, 
                          current_app.config.get('LDAP_BIND_DN', ''),
                          current_app.config.get('LDAP_BIND_PASSWORD', ''),
                          auto_bind=True) as conn:
                
                conn.search(
                    search_base=current_app.config['LDAP_USER_DN'],
                    search_filter=search_filter,
                    search_scope=SUBTREE,
                    attributes=['cn', 'mail', 'department', 'memberOf']
                )
                
                if not conn.entries:
                    logger.warning(f"User {username} not found in LDAP")
                    return None
                
                user_dn = conn.entries[0].entry_dn
                
            # Попытка привязки с учетными данными пользователя
            with Connection(server, user_dn, password, auto_bind=True) as user_conn:
                # Успешная аутентификация
                user_info = conn.entries[0]
                
                # Получение роли из групп AD
                role = 'Viewer'
                member_of = user_info.memberOf.values if hasattr(user_info, 'memberOf') else []
                
                if current_app.config['LDAP_ADMIN_GROUP'] in member_of:
                    role = 'Admin'
                elif current_app.config['LDAP_EDITOR_GROUP'] in member_of:
                    role = 'Editor'
                
                # Создание/обновление пользователя в БД
                user = User.query.filter_by(username=username).first()
                if not user:
                    user = User(
                        username=username,
                        display_name=str(user_info.cn),
                        email=str(user_info.mail) if hasattr(user_info, 'mail') else username,
                        department=str(user_info.department) if hasattr(user_info, 'department') else '',
                        role=role
                    )
                else:
                    user.display_name = str(user_info.cn)
                    user.email = str(user_info.mail) if hasattr(user_info, 'mail') else username
                    user.department = str(user_info.department) if hasattr(user_info, 'department') else ''
                    user.role = role
                
                db.session.add(user)
                db.session.commit()
                
                return user
                
        except LDAPException as e:
            logger.error(f"LDAP authentication error for {username}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            return None