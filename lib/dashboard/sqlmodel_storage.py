import json
from typing import Any

from dachshund.storage.protocol import SyncStorage

from bot.models.extensions.widget_state import WidgetState


class SQLModelStorage(SyncStorage):
    def _save(self, key: str, value: dict[str, Any]) -> None:
        record = WidgetState.find(key)

        if record is None:
            WidgetState.create(key=key, value=json.dumps(value))
        else:
            record.update(value=json.dumps(value))

    def _load(self, key: str) -> dict[str, Any] | None:
        record = WidgetState.find(key)
        return json.loads(record.value) if record else None
