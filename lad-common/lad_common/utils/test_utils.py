import pytest


def generate_test_app_fixture(init_app):
    @pytest.fixture
    def test_app_fixture():
        app = init_app()
        with app.app_context():
            yield app

    return test_app_fixture
