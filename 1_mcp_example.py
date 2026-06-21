import asyncio, json, time
from dataclasses import dataclass, field
from typing import Dict, Any
from enum import Enum

class MCPRole(Enum):
    HOST = "host"
    CLIENT = "client"
    SERVER = "server"


@dataclass
class MCPCapabilities:
    tools: bool = True
    resources: bool = True
    prompts: bool = True
    logging: bool = False
    experimental: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.tools:
            result["tools"] = {}
        if self.resources:
            result["resources"] = {}
        if self.prompts:
            result["prompts"] = {}
        if self.logging:
            result["logging"] = {}
        if self.experimental:
            result["experimental"] = self.experimental
        return result

@dataclass
class PendingRequest:
    id: int
    method: str
    sent_at: float
    future: asyncio.Future

class MCPError:
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

@dataclass
class RequestTracker:
    pending: Dict[int, PendingRequest] = field(default_factory=dict)
    timeout: float = 30.0
    _next_id: int = 0

    def create_request(self, method: str, params: Dict[str, Any]) -> tuple[int, Dict]:
        self._next_id += 1
        req_id = self._next_id
        request = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        future = asyncio.get_event_loop().create_future()
        self.pending[req_id] = PendingRequest(id=req_id, method=method,
                                              sent_at=time.time(), future=future)
        return req_id, request

    def handle_response(self, response: Dict[str, Any]) -> bool:
        req_id = response.get("id")
        if req_id is None or req_id not in self.pending:
            return False
        pending = self.pending.pop(req_id)
        if "error" in response:
            err = response["error"]
            pending.future.set_exception(
                MCPError(code=err["code"], message=err["message"], data=err.get("data"))
            )
        else:
            pending.future.set_result(response.get("result"))
        return True


async def _run_request_tracker_test() -> None:
    tracker = RequestTracker()
    req_id, request = tracker.create_request("tools/call", {"name": "echo", "arguments": {}})
    assert req_id == 1
    assert request == {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "echo", "arguments": {}},
    }

    pending = tracker.pending.get(req_id)
    if pending is None:
        raise RuntimeError("Pending request not found before response handling")

    response = {"jsonrpc": "2.0", "id": 1, "result": {"content": "ok"}}
    handled = tracker.handle_response(response)
    assert handled is True

    result = await asyncio.wait_for(pending.future, timeout=1.0)
    assert result == {"content": "ok"}
    print("Request/response correlation succeeded:", result)


if __name__ == "__main__":
    asyncio.run(_run_request_tracker_test())