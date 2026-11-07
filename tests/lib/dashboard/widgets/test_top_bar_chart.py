import pytest
from dachshund.storage.events import Event

from lib.dashboard.widgets.top_bar_chart import TopBarChart


def _events(*emojis):
    return [Event("emojis", {"emoji": emoji, "value": 1}) for emoji in emojis]


def test_render__expect_biggest_bars_first():
    chart = TopBarChart("emojis", x="emoji")

    payload = chart.render(_events("👍", "🔥", "👍", "🎉", "👍", "🔥"))

    assert payload["x"] == ["👍", "🔥", "🎉"]
    assert payload["y"] == [[3.0, 2.0, 1.0]]


def test_render__with_more_than_top__expect_only_the_biggest():
    chart = TopBarChart("emojis", x="emoji", top=2)

    payload = chart.render(_events("a", "b", "b", "c", "c", "c"))

    assert payload["x"] == ["c", "b"]


def test_top__below_one__expect_error():
    with pytest.raises(ValueError, match="top"):
        TopBarChart("emojis", x="emoji", top=0)
