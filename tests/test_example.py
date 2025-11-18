"""
Example test file

Run tests with:
    pytest
"""


def test_example():
    """Example test"""
    assert 1 + 1 == 2


def test_backend_imports():
    """Test that backend modules can be imported"""
    from app import config, database, models, schemas, auth
    assert config is not None
    assert database is not None
    assert models is not None
    assert schemas is not None
    assert auth is not None

