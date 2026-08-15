import pytest
from unittest.mock import AsyncMock

from bot.extensions.grace_cog import GraceCog


@pytest.fixture
def grace_cog(mock_bot):
    """Instantiate the GraceCog with a mock bot."""
    mock_bot.latency_ms = 50
    return GraceCog(mock_bot)


@pytest.mark.asyncio
async def test_ping_command__expect_records_latency_and_shows_it(grace_cog):
    """Verify ping_command reads the bot's latency, records it, and shows it to the user."""
    ctx = AsyncMock()

    await grace_cog.ping_command.callback(grace_cog, ctx)

    grace_cog.bot.metrics.record_latency.assert_called_once_with(
        50, is_from_command=True
    )

    embed = ctx.send.call_args[1]["embed"]
    assert "50ms" in embed.description
