from unittest.mock import patch

from bot.services.random_name_service import make_random_name

@patch("random.choice")
def test_random_name_service__expect_normal_output(mock_random):
    mock_random.side_effect = ["good", "grace"]

    assert make_random_name() == "Good Grace"

    assert mock_random.call_count == 2
