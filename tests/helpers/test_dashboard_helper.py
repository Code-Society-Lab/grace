from unittest.mock import patch

from freezegun import freeze_time

from bot.helpers.dashboard_helper import MODERATION_SOURCE, record_moderation, timestamp


def test_timestamp__expect_eastern_time():
    with freeze_time("2025-02-21 03:00:00"):
        assert timestamp() == "2025-02-20 22:00:00"


@patch("bot.helpers.dashboard_helper.dachshund.emit")
def test_record_moderation__expect_a_timestamped_row(mock_emit):
    with freeze_time("2025-02-21 03:00:00"):
        record_moderation("purge", by="mod", details="5 message(s)")

    mock_emit.assert_called_once_with(
        MODERATION_SOURCE,
        time="2025-02-20 22:00:00",
        action="purge",
        member="",
        by="mod",
        details="5 message(s)",
    )


@patch("bot.helpers.dashboard_helper.dachshund.emit")
def test_record_moderation__without_moderator__expect_auto(mock_emit):
    record_moderation("kick", member="spammer")

    assert mock_emit.call_args.kwargs["by"] == "auto"
