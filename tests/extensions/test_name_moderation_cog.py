from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord import Embed
from bot.extensions.name_moderation_cog import *


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
@patch("bot.extensions.name_moderation_cog.slice_name")
async def test_name_moderation_on_member_join__with_normal_name__expect_nothing(
    mock_slice, mock_random, mock_notice, name_moderation_cog
):
    member = AsyncMock()
    member.display_name = "Normal Name"

    mock_slice.return_value = ["Name"]

    name_moderation_cog.BAD_WORDS = ["Nothing"]
    await name_moderation_cog.on_member_join(member)

    mock_slice.assert_called_once_with("Normal Name")
    mock_random.assert_not_called()
    member.edit.assert_not_awaited()
    member.send.assert_not_awaited()
    mock_notice.assert_not_called()


@pytest.mark.asyncio
@patch("bot.extensions.name_moderation_cog.notice")
@patch("bot.extensions.name_moderation_cog.make_random_name")
@patch("bot.extensions.name_moderation_cog.slice_name")
async def test_name_moderation_on_member_join__with_bad_name__expect_change_and_message(
    mock_slice, mock_random, mock_notice, name_moderation_cog
):
    member = AsyncMock()
    member.display_name = "Bad Name"

    mock_log = MagicMock()
    mock_notice.return_value = mock_log
    mock_log.send = AsyncMock()

    mock_slice.return_value = ["Bad"]
    mock_random.return_value = "Good Name"

    name_moderation_cog.BAD_WORDS = ["Bad"]

    await name_moderation_cog.on_member_join(member)

    mock_slice.assert_called_once_with("Bad Name")

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


@pytest.mark.asyncio
@patch("bot.extensions.name_moderation_cog.make_random_name")
async def test_name_moderation_give_random_name__expect_random_name(
    mock_random, mock_bot, mock_ctx, name_moderation_cog
):
    mock_ctx.author.display_name = "Old name"
    mock_ctx.author.edit = AsyncMock()
    mock_random.return_value = "New name"

    await name_moderation_cog.give_random_name(name_moderation_cog, mock_ctx)

    result = Embed(title="Name Changed!", color=mock_bot.default_color)
    result.description = "Your name was changed from Old name to New name!"

    mock_random.assert_called_once()
    mock_ctx.author.edit.assert_awaited_once_with(nick="New name")
    mock_ctx.send.assert_awaited_once_with(embed=result)


@pytest.mark.parametrize(
    ("slices, bad_word_set, output"),
    [
        [["Name"], {"Stuff"}, False],
        [["Name"], {"Name"}, True],
        [["Name"], {"Stuff", "Name"}, True],
        [["Stuff", "Name"], {"Stuff", "Name"}, True],
    ],
)
def test_check_slices__expecgtg_matching_output(
    slices, bad_word_set, output, name_moderation_cog
):
    name_moderation_cog.BAD_WORDS = bad_word_set

    assert name_moderation_cog.check_slices_against_bad_words(slices) == output


@pytest.mark.parametrize(
    ("input_name, output_list"),
    [
        ["a", []],
        ["ab", []],
        ["abc", ["abc"]],
        ["🐔b1%", ["🐔b1", "🐔b1%", "b1%"]],
    ],
)
def test_slice_name__with_normal_input__expect_matching_output(input_name, output_list):
    assert slice_name(input_name) == output_list


@pytest.mark.parametrize(
    ("input_name, output_list"),
    [
        ["aBc", ["abc"]],
        ["AbC", ["abc"]],
        ["ABc", ["abc"]],
        ["ABC", ["abc"]],
        ["AB1🐔", ["ab1", "ab1🐔", "b1🐔"]],
    ],
)
def test_slice_name__with_uppercase_input__expect_case_insensitive_output(
    input_name, output_list
):
    assert slice_name(input_name) == output_list
