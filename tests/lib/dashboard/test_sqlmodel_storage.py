import pytest

from bot.models.extensions.widget_state import WidgetState
from lib.dashboard.sqlmodel_storage import SQLModelStorage


@pytest.fixture
def storage():
    """Instantiate SQLModelStorage backed by the test database."""
    return SQLModelStorage()


@pytest.mark.asyncio
async def test_load__with_no_saved_value__expect_none(storage):
    """Verify load returns None for a key that was never saved."""
    result = await storage.load("missing")

    assert result is None


@pytest.mark.asyncio
async def test_save__expect_value_is_loadable(storage):
    """Verify a saved value can be read back through load."""
    await storage.save("on_command", {"totals": {"/ping": 3}})
    result = await storage.load("on_command")

    assert result == {"totals": {"/ping": 3}}


@pytest.mark.asyncio
async def test_save__with_existing_key__expect_value_replaced(storage):
    """Verify saving under an existing key replaces it rather than duplicating it."""
    await storage.save("on_command", {"totals": {"/ping": 1}})
    await storage.save("on_command", {"totals": {"/ping": 2}})

    result = await storage.load("on_command")

    assert result == {"totals": {"/ping": 2}}
    assert WidgetState.where(key="on_command").count() == 1
