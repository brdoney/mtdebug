from typing import Any
from flask.json.provider import DefaultJSONProvider
from action_tracker import Resource

from tlv_server import LibcAction, TLVMessage, TLVTag


class CustomEncoder(DefaultJSONProvider):
    @staticmethod
    def default(obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, TLVTag):
            return obj.name
        elif isinstance(obj, Resource | LibcAction | TLVMessage):
            return obj.__dict__
        return super(CustomEncoder, CustomEncoder).default(obj)

    def dumps(self, obj: Any, **kwargs: Any) -> str:
        return super().dumps(obj, default=self.default, **kwargs)
