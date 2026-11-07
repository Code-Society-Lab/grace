from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.extensions.moderation_cog import ModerationCog


@pytest.fixture
def moderation_cog(mock_bot):
    mock_bot.get_channel_by_name.return_value = None
    return ModerationCog(mock_bot)


def _member(account_age_days):
    member = AsyncMock()
    member.created_at = datetime.now(tz=UTC) - timedelta(days=account_age_days)
    member.guild.kick = AsyncMock()
    return member


@pytest.mark.asyncio
@patch("bot.extensions.moderation_cog.danger")
@patch("bot.extensions.moderation_cog.app.config.get", return_value=30)
@patch("bot.extensions.moderation_cog.dachshund.emit")
async def test_on_member_join__with_young_account__expect_kick_row(
    mock_emit, _config, _danger, moderation_cog
):
    member = _member(account_age_days=2)

    await moderation_cog.on_member_join(member)

    member.guild.kick.assert_awaited_once()
    mock_emit.assert_called_once_with(
        "recent_moderation",
        action="kick",
        member=str(member),
        by="auto",
        details="account 2 day(s) old, minimum 30",
    )


@pytest.mark.asyncio
@patch("bot.extensions.moderation_cog.app.config.get", return_value=30)
@patch("bot.extensions.moderation_cog.dachshund.emit")
async def test_on_member_join__with_old_account__expect_no_row(
    mock_emit, _config, moderation_cog
):
    member = _member(account_age_days=365)

    await moderation_cog.on_member_join(member)

    member.guild.kick.assert_not_awaited()
    mock_emit.assert_not_called()


@pytest.mark.asyncio
@patch("bot.extensions.moderation_cog.danger")
@patch("bot.extensions.moderation_cog.dachshund.emit")
async def test_purge__expect_purge_row_by_its_moderator(
    mock_emit, mock_danger, moderation_cog
):
    mock_danger.return_value = MagicMock(send=AsyncMock())
    ctx = MagicMock()
    ctx.defer = AsyncMock()
    ctx.channel.purge = AsyncMock()
    ctx.channel.__str__ = lambda _: "general"
    ctx.author.__str__ = lambda _: "mod"

    await moderation_cog.purge.callback(moderation_cog, ctx, 5, "spam")

    ctx.channel.purge.assert_awaited_once()
    mock_emit.assert_called_once_with(
        "recent_moderation",
        action="purge",
        member="",
        by="mod",
        details="5 message(s) in #general · spam",
    )
