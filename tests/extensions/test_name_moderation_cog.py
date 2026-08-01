from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bot.extensions.name_moderation_cog import NameModerationCog


@pytest.fixture
def name_moderation_cog(mock_bot):
    """Instantiate the NameModerationCog with a mock bot."""

    mock_bot.get_channel_by_name.return_value = "Mod room"

    return NameModerationCog(mock_bot)


@pytest.fixture
def mock_ctx():
    """Create a mock command context."""
    ctx = MagicMock()
    ctx.defer = AsyncMock()
    ctx.send = AsyncMock()
    return ctx


@pytest.mark.asyncio
@patch("bot.extensions.name_moderation_cog.notice")
@patch("bot.extensions.name_moderation_cog.make_random_name")
async def test_name_moderation_on_member_join__with_none_blacklisted_name__expect_nothing(
    mock_random, mock_notice, name_moderation_cog
):
    member = AsyncMock()
    member.display_name = "Normal Name"

    name_moderation_cog.BAD_WORDS = ["nothing"]
    await name_moderation_cog.on_member_join(member)

    mock_random.assert_not_called()
    member.edit.assert_not_awaited()
    member.send.assert_not_awaited()
    mock_notice.assert_not_called()


@pytest.mark.asyncio
@patch("bot.extensions.name_moderation_cog.notice")
@patch("bot.extensions.name_moderation_cog.make_random_name")
async def test_name_moderation_on_member_join__with_blacklisted_name__expect_change_and_message(
    mock_random, mock_notice, name_moderation_cog
):
    member = AsyncMock()
    member.display_name = "Bad Name"

    mock_log = MagicMock()
    mock_notice.return_value = mock_log
    mock_log.send = AsyncMock()

    mock_random.return_value = "Good Name"

    name_moderation_cog.BAD_WORDS = ["bad"]

    await name_moderation_cog.on_member_join(member)

    mock_random.assert_called_once()

    member.edit.assert_awaited_once_with(nick="Good Name")
    member.send.assert_awaited_once_with(
        "Your name has an inappropriate word in it, thus it was changed from Bad Name to Good Name."
    )

    mock_notice.assert_called_once_with("NAME", "Username of Bad Name was changed.")
    mock_log.add_field.assert_called_once_with(
        "Reason: ",
        "User Bad Name joined with an inappropriate name, thus it was changed to Good Name.",
    )
    mock_log.send.assert_awaited_once_with("Mod room")
