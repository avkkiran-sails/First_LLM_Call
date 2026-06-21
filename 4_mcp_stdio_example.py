import asyncio
import json
import logging
import sys
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@dataclass
class StdioTransportConfig:
    """Configuration for stdio transport."""
    command: str
    args: List[str] = field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None


class StdioTransport:
    """Stdio transport for MCP: subprocess + stdin/stdout JSON-RPC."""

    def __init__(self, config: StdioTransportConfig):
        self.config = config
        self.process: Optional[asyncio.subprocess.Process] = None
        self._read_task: Optional[asyncio.Task] = None
        self._stderr_task: Optional[asyncio.Task] = None
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        print(f"[MCP] Initialized transport for command: {self.config.command} {self.config.args}")

    async def start(self) -> None:
        if self.process is not None:
            raise RuntimeError("Transport already started")
        cmd = [self.config.command] + self.config.args
        print(f"[MCP] Starting subprocess: {cmd}")
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=self.config.env,
            cwd=self.config.cwd,
        )
        self._running = True
        self._read_task = asyncio.create_task(self._read_loop())
        self._stderr_task = asyncio.create_task(self._stderr_loop())
        logger.info("Started MCP server: %s", self.config.command)
        print(f"[MCP] Transport started and read loop task created (pid={self.process.pid})")

    async def stop(self) -> None:
        print("[MCP] Stopping transport")
        self._running = False
        if self._read_task:
            print("[MCP] Cancelling read loop task")
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                print("[MCP] Read loop task cancelled")
        if self._stderr_task:
            print("[MCP] Cancelling stderr monitor task")
            self._stderr_task.cancel()
            try:
                await self._stderr_task
            except asyncio.CancelledError:
                print("[MCP] Stderr monitor task cancelled")
        if self.process:
            print("[MCP] Terminating subprocess")
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                print("[MCP] Killing subprocess after timeout")
                self.process.kill()
                await self.process.wait()
        logger.info("Stopped MCP server")
        print("[MCP] Transport stopped")

    async def send(self, message: Dict[str, Any]) -> None:
        if not self.process or not self.process.stdin:
            raise RuntimeError("Transport not started")
        data = json.dumps(message) + "\n"
        print(f"[MCP] Sending message: {data.strip()}")
        self.process.stdin.write(data.encode())
        await self.process.stdin.drain()

    async def receive(self) -> Optional[Dict[str, Any]]:
        print("[MCP] Waiting to receive a message from the read loop")
        message = await self._message_queue.get()
        if message is None:
            print("[MCP] Received shutdown sentinel from queue")
            return None
        print(f"[MCP] Received message: {json.dumps(message)}")
        return message

    async def _read_loop(self) -> None:
        print("[MCP] Read loop started")
        try:
            while self._running and self.process and self.process.stdout:
                line = await self.process.stdout.readline()
                if not line:
                    print("[MCP] Read loop detected EOF")
                    break
                raw_line = line.decode().rstrip("\n")
                print(f"[MCP] Read raw line: {raw_line}")
                try:
                    message = json.loads(raw_line)
                    print(f"[MCP] Parsed JSON message: {message}")
                    await self._message_queue.put(message)
                except json.JSONDecodeError as e:
                    logger.warning("Failed to parse message: %s", e)
                    print(f"[MCP] Failed to parse JSON line: {raw_line}")
        except asyncio.CancelledError:
            print("[MCP] Read loop cancelled")
            pass
        except Exception as e:
            logger.error("Read loop error: %s", e)
            print(f"[MCP] Read loop error: {e}")
        finally:
            print("[MCP] Read loop exiting and sending shutdown sentinel")
            await self._message_queue.put(None)

    async def _stderr_loop(self) -> None:
        print("[MCP] Stderr monitor started")
        try:
            while self._running and self.process and self.process.stderr:
                line = await self.process.stderr.readline()
                if not line:
                    break
                print(f"[MCP][stderr] {line.decode(errors='replace').rstrip()}" )
        except asyncio.CancelledError:
            print("[MCP] Stderr monitor cancelled")
            pass
        except Exception as e:
            print(f"[MCP] Stderr monitor error: {e}")


async def main() -> None:
    config = StdioTransportConfig(
        command=sys.executable,
        args=["-u", "-c", "import json; print(json.dumps({'id': 1, 'result': 'pong'}), flush=True)"],
    )
    transport = StdioTransport(config)

    await transport.start()

    request = {"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {"message": "hello"}}
    await transport.send(request)

    response = await transport.receive()
    print(f"[MCP] Example received response: {response}")

    await transport.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[MCP] Interrupted by user")