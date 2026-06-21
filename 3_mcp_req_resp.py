from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
import asyncio


@dataclass
class JSONRPCRequest:
    """A JSON-RPC 2.0 request: method AND id; expects a response."""
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"jsonrpc": "2.0", "method": self.method}
        if self.params is not None:
            result["params"] = self.params
        if self.id is not None:
            result["id"] = self.id
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JSONRPCRequest":
        if data.get("jsonrpc") != "2.0":
            raise ValueError("Invalid JSON-RPC version")
        return cls(
            method=data["method"],
            params=data.get("params"),
            id=data.get("id"),
        )


# Standard MCP method names grouped by category.
MCP_METHODS = {
    "initialize": "Initialize the connection and exchange capabilities",
    "shutdown": "Request graceful shutdown",
    "tools/list": "List available tools",
    "tools/call": "Invoke a specific tool",
    "resources/list": "List available resources",
    "resources/read": "Read a specific resource",
    "resources/subscribe": "Subscribe to resource updates",
    "prompts/list": "List available prompt templates",
    "prompts/get": "Get a specific prompt template",
    "logging/setLevel": "Set the logging level",
    "completion/complete": "Request completion suggestions",
}



@dataclass
class JSONRPCError:
    """A JSON-RPC 2.0 error object."""
    code: int
    message: str
    data: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result


class ErrorCode:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


@dataclass
class JSONRPCResponse:
    """Response: id matches request; exactly one of result OR error."""
    id: int
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None

    def __post_init__(self) -> None:
        if self.result is not None and self.error is not None:
            raise ValueError("Response cannot have both result and error")

    def to_dict(self) -> Dict[str, Any]:
        response: Dict[str, Any] = {"jsonrpc": "2.0", "id": self.id}
        if self.error is not None:
            response["error"] = self.error.to_dict()
        else:
            response["result"] = self.result
        return response

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JSONRPCResponse":
        error = None
        if "error" in data:
            err = data["error"]
            error = JSONRPCError(
                code=err["code"],
                message=err["message"],
                data=err.get("data"),
            )
        return cls(id=data["id"], result=data.get("result"), error=error)


@dataclass
class JSONRPCNotification:
    """Notification: method, NO id; fire-and-forget."""
    method: str
    params: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"jsonrpc": "2.0", "method": self.method}
        if self.params is not None:
            result["params"] = self.params
        return result


def is_request(msg: Dict[str, Any]) -> bool:
    return "method" in msg and "id" in msg


def is_response(msg: Dict[str, Any]) -> bool:
    return "id" in msg and "method" not in msg


def is_notification(msg: Dict[str, Any]) -> bool:
    return "method" in msg and "id" not in msg


def print_response_summary(response: JSONRPCResponse) -> None:
    if response.error is not None:
        print("❌ Negative response detected:")
        print(f"  id: {response.id}")
        print(f"  error.code: {response.error.code}")
        print(f"  error.message: {response.error.message}")
        if response.error.data is not None:
            print(f"  error.data: {response.error.data}")
    else:
        print("✅ Positive response detected:")
        print(f"  id: {response.id}")
        print(f"  result: {response.result}")


async def send_request(request: JSONRPCRequest) -> JSONRPCResponse:
    print("--- Sending request ---")
    print(json.dumps(request.to_dict(), indent=2))
    await asyncio.sleep(0.2)

    if request.method == "echo":
        return JSONRPCResponse(id=request.id or 0, result={"echo": request.params})

    if request.method == "sum":
        if not isinstance(request.params, dict) or "a" not in request.params or "b" not in request.params:
            return JSONRPCResponse(
                id=request.id or 0,
                error=JSONRPCError(
                    code=ErrorCode.INVALID_PARAMS,
                    message="Missing required params 'a' and 'b'",
                ),
            )
        return JSONRPCResponse(
            id=request.id or 0,
            result={"sum": request.params["a"] + request.params["b"]},
        )

    return JSONRPCResponse(
        id=request.id or 0,
        error=JSONRPCError(
            code=ErrorCode.METHOD_NOT_FOUND,
            message=f"Unknown method: {request.method}",
        ),
    )


def send_notification(notification: JSONRPCNotification) -> None:
    print("--- Sending notification ---")
    print(json.dumps(notification.to_dict(), indent=2))
    print("Notification sent. No response expected.\n")


async def main() -> None:
    request = JSONRPCRequest(method="sum", params={"a": 5, "b": 7}, id=101)
    response = await send_request(request)
    print_response_summary(response)
    print()

    bad_request = JSONRPCRequest(method="sum", params={"a": 5}, id=102)
    bad_response = await send_request(bad_request)
    print_response_summary(bad_response)
    print()

    notification = JSONRPCNotification(method="notify/event", params={"message": "Hello from notification"})
    send_notification(notification)


if __name__ == "__main__":
    asyncio.run(main())
