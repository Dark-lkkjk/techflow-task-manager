import pytest
from src.app import create_app
from src.models import db as _db


@pytest.fixture(scope='function')
def app():
    """Cria uma instância da aplicação configurada para testes (banco em memória)."""
    cfg = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }
    application = create_app(cfg)

    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Cliente HTTP para testar os endpoints da API."""
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """Fornece acesso à sessão de banco de dados durante os testes."""
    with app.app_context():
        yield _db
