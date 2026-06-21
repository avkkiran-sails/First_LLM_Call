import asyncio
import aiohttp
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
from aiohttp import web

@dataclass
class HTTPTransportConfig:
    base_url: str
    headers: Optional[Dict[str, str]] = None
    timeout: float = 30.0

class HTTPTransport:
    def __init__(self, config: HTTPTransportConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._sse_task: Optional[asyncio.Task] = None
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def start(self) -> None:
        headers = {**(self.config.headers or {}), "Content-Type": "application/json"}
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        self._running = True
        self._sse_task = asyncio.create_task(self._sse_loop())

    async def stop(self) -> None:
        self._running = False
        if self._sse_task:
            self._sse_task.cancel()
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass
        if self.session:
            await self.session.close()

    async def send(self, message: Dict[str, Any]) -> Dict[str, Any]:
        if not self.session:
            raise RuntimeError("Transport not started")
        async with self.session.post(
            f"{self.config.base_url}/message", json=message
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def receive(self) -> Dict[str, Any]:
        return await self._message_queue.get()

    async def _sse_loop(self) -> None:
        if not self.session:
            return
        try:
            async with self.session.get(f"{self.config.base_url}/sse/test-2") as response:
                async for line in response.content:
                    if not self._running:
                        break
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        try:
                            await self._message_queue.put(json.loads(line[6:]))
                        except json.JSONDecodeError as e:
                            logger.warning(f"Invalid SSE data: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"SSE loop error: {e}")


async def start_mock_server(host: str = "127.0.0.1", port: int = 8000) -> web.AppRunner:
    app = web.Application()
    app["sse_clients"] = []

    async def sse(request: web.Request) -> web.StreamResponse:
        resp = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            },
        )
        await resp.prepare(request)
        q: asyncio.Queue = asyncio.Queue()
        app["sse_clients"].append(q)
        try:
            while True:
                msg = await q.get()
                await resp.write(f"data: {json.dumps(msg)}\n\n".encode())
        except asyncio.CancelledError:
            pass
        finally:
            try:
                app["sse_clients"].remove(q)
            except ValueError:
                pass
        return resp

    async def post_message(request: web.Request) -> web.Response:
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "invalid json"}, status=400)
        # accept an optional parameter from the JSON body or query string
        param = None
        if isinstance(data, dict):
            param = data.get("param")
        if param is None:
            param = request.query.get("param")

        # broadcast to clients
        for q in list(app["sse_clients"]):
            try:
                q.put_nowait(data)
            except Exception:
                pass

        # build concatenated echo using the provided parameter
        if param:
            echo = f"{param} Hello from client"
        else:
            echo = "Hello from client"

        return web.json_response({"status": "ok", "echo": echo})

    app.router.add_get('/sse', sse)
    app.router.add_post('/message', post_message)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    return runner


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    # Update base_url to point to your MCP HTTP SSE server if needed
    config = HTTPTransportConfig(base_url="http://localhost:8080/mcp")

    # Start a local mock server for testing
    # mock_runner = await start_mock_server(host="127.0.0.1", port=8080)
    transport = HTTPTransport(config)
    await transport.start()
    try:
        request = {"id": "test-2", "requestId": "test-2", "type": "request", "content": "What is Model Context Protocol in 2 lines?"}
        # print("Request:", json.dumps(request))
        # Send the request and print the immediate HTTP response
        response = await transport.send(request)
        # print("Response:", json.dumps(response))

        # Try to read any SSE message emitted by the server (with timeout)
        try:
            sse_msg = await asyncio.wait_for(transport.receive(), timeout=25.0)
            print("SSE message:", json.dumps(sse_msg))
        except asyncio.TimeoutError:
            print("No SSE messages received within timeout.")
    finally:
        await transport.stop()
        # Shutdown mock server
        # await mock_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())