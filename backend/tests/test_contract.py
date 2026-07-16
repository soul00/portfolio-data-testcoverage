import pytest
import schemathesis

from quality_gate.api import app
from quality_gate.storage import create_tables

schema = schemathesis.openapi.from_asgi("/openapi.json", app)


@pytest.fixture(autouse=True, scope="module")
def tables():
    create_tables()


@schema.parametrize()
def test_api_contract(case):
    case.call_and_validate()
