import pytest

from lad_crm.app import init_app
from lad_common.utils.test_utils import generate_test_app_fixture


test_app = generate_test_app_fixture(init_app)


@pytest.fixture
def test_client(test_app):
    with test_app.test_client() as client:
        yield client
