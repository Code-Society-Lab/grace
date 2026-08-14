from unittest.mock import patch

import pytest

from bot.extensions.grace_cog import GraceCog


@pytest.fixture
def grace_cog(mock_bot):
    """Instantiate the GraceCog with a mock bot."""
    mock_bot.latency = 0.05
    return GraceCog(mock_bot)


@patch("bot.extensions.grace_cog.dachshund.emit")
def test_check_latency__expect_emits_latency(mock_emit, grace_cog):
    """Verify check_latency always emits a latency event."""
    latency_ms = grace_cog.check_latency()

    assert latency_ms == 50
    mock_emit.assert_any_call("latency", check=50, command=None)


@patch("bot.extensions.grace_cog.dachshund.emit")
def test_check_latency__with_is_from_command__expect_emits_command_latency(
    mock_emit, grace_cog
):
    """Verify check_latency records the command latency when triggered by a command."""
    grace_cog.check_latency(is_from_command=True)

    mock_emit.assert_any_call("latency", check=50, command=50)


@patch("bot.extensions.grace_cog.dachshund.emit")
def test_check_latency__with_new_max__expect_emits_highest_latency(
    mock_emit, grace_cog
):
    """Verify highest_latency is emitted when a new maximum is reached."""
    grace_cog.check_latency()

    assert mock_emit.call_args_list[-1].args[0] == "highest_latency"


@patch("bot.extensions.grace_cog.dachshund.emit")
def test_check_latency__with_lower_latency__expect_no_highest_latency_emit(
    mock_emit, grace_cog
):
    """Verify highest_latency is not re-emitted when latency stays below the max."""
    grace_cog.check_latency()
    mock_emit.reset_mock()

    grace_cog.bot.latency = 0.02
    grace_cog.check_latency()

    assert mock_emit.call_count == 1
    assert mock_emit.call_args.args[0] == "latency"


@pytest.mark.asyncio
@patch("bot.extensions.grace_cog.dachshund.emit")
async def test_on_command__expect_emits_command_name(mock_emit, grace_cog):
    """Verify on_command emits the qualified command name."""
    ctx = type("Ctx", (), {"command": type("Cmd", (), {"qualified_name": "ping"})()})()

    await grace_cog.on_command(ctx)

    mock_emit.assert_called_once_with("on_command", name="ping", value=1)
