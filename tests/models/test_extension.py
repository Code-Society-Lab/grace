from bot.classes.state import State
from bot.models.extension import Extension


def test_create_extension():
    """Test creating an extension"""
    extension = Extension.create(module_name='test_extension', state=State.ENABLED)

    assert extension.module_name == 'test_extension'
    assert extension.state == State.ENABLED


def test_get_extension():
    """Test getting an extension"""
    extension = Extension.get_by(module_name='test_extension')

    assert Extension.get(extension.id) == extension


def test_disable_extension():
    """Test disabling an extension"""
    extension = Extension.get_by(module_name='test_extension')
    extension.state = State.DISABLED

    assert extension.state == State.DISABLED


def test_enable_extension():
    """Test enabling an extension"""
    extension = Extension.get_by(module_name='test_extension')
    extension.state = State.ENABLED

    assert extension.state == State.ENABLED


def test_get_by_state():
    """Test getting extensions by state"""
    extensions = Extension.by_state(State.ENABLED)

    assert extensions.count() > 0


def test_delete_extension():
    """Test deleting an extension"""
    extension = Extension.get_by(module_name='test_extension')
    extension.delete()

    assert Extension.get(extension.id) is None
