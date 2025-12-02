import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Базовая конфигурация."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dash5s.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LDAP / AD Configuration
    LDAP_SERVER = os.environ.get('LDAP_SERVER', 'localhost')
    LDAP_PORT = int(os.environ.get('LDAP_PORT', 389))
    LDAP_USE_SSL = os.environ.get('LDAP_USE_SSL', 'false').lower() == 'true'
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', 'dc=test,dc=local')
    LDAP_USER_DN = os.environ.get('LDAP_USER_DN', 'ou=users,dc=test,dc=local')
    LDAP_GROUP_DN = os.environ.get('LDAP_GROUP_DN', 'ou=groups,dc=test,dc=local')
    LDAP_USER_RDN_ATTR = os.environ.get('LDAP_USER_RDN_ATTR', 'cn')
    LDAP_USER_LOGIN_ATTR = os.environ.get('LDAP_USER_LOGIN_ATTR', 'mail')
    
    # Default AD Groups for roles mapping
    LDAP_ADMIN_GROUP = os.environ.get('LDAP_ADMIN_GROUP', 'cn=Dash5S_Admins,ou=groups,dc=test,dc=local')
    LDAP_EDITOR_GROUP = os.environ.get('LDAP_EDITOR_GROUP', 'cn=Dash5S_Editors,ou=groups,dc=test,dc=local')
    