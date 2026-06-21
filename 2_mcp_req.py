import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    INVALID = "invalid"


@dataclass
class ParsedMessage:
    type: MessageType
    data: Optional[Dict[str, Any]]
    raw: str
    error: Optional[str] = None


class MessageParser:
    def parse(self, raw: str) -> ParsedMessage:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            return ParsedMessage(
                type=MessageType.INVALID, data=None, raw=raw,
                error=f"JSON parse error: {e}"
            )
        if data.get("jsonrpc") != "2.0":
            return ParsedMessage(
                type=MessageType.INVALID, data=data, raw=raw,
                error="Missing or invalid jsonrpc version"
            )
        return ParsedMessage(type=self._classify(data), data=data, raw=raw)

    def _classify(self, data: Dict[str, Any]) -> MessageType:
        has_method = "method" in data
        has_id = "id" in data
        if has_method and has_id:
            return MessageType.REQUEST
        elif has_method:
            return MessageType.NOTIFICATION
        elif has_id:
            return MessageType.RESPONSE
        return MessageType.INVALID
    
@dataclass
class MessageHandler:
    request_handlers: Dict[str, Callable] = field(default_factory=dict)
    notification_handlers: Dict[str, Callable] = field(default_factory=dict)

    def register_request(self, method: str, handler: Callable) -> None:
        self.request_handlers[method] = handler

    def register_notification(self, method: str, handler: Callable) -> None:
        self.notification_handlers[method] = handler

    def handle(self, msg: ParsedMessage) -> Optional[Dict[str, Any]]:
        if msg.type == MessageType.INVALID:
            return {"jsonrpc": "2.0", "error": {"code": -32600, "message": msg.error}}
        if msg.type == MessageType.NOTIFICATION:
            handler = self.notification_handlers.get(msg.data["method"])
            if handler:
                handler(msg.data)
            return None
        if msg.type == MessageType.REQUEST:
            handler = self.request_handlers.get(msg.data["method"])
            if handler:
                return handler(msg.data)
        return None


# Wire up a ping handler and exercise both components
parser = MessageParser()
router = MessageHandler()
router.register_request(
    "ping",
    lambda msg: {"jsonrpc": "2.0", "id": msg["id"], "result": "pong"}
)

raw = '{"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {}}'
parsed = parser.parse(raw)
response = router.handle(parsed)
print(response)