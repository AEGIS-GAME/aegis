# pyright: reportMissingTypeStubs = false
import base64
import queue
import threading
import time
from typing import NamedTuple

from websocket_server import WebsocketServer

from .logger import LOGGER


class Client(NamedTuple):
    """Represents a connected client."""

    id: int
    handler: object
    address: str


class WebSocketServer:
    def __init__(self, *, wait_for_client: bool) -> None:
        """Initialize a new server."""
        self._host: str = "localhost"
        self._port: int = 6003
        self._wait_for_client: bool = wait_for_client
        self._connected: bool = False
        self._done: bool = False
        self._server: WebsocketServer | None = None
        self._previous_events: list[str] = []
        self._incoming_events: queue.Queue[str] = queue.Queue()
        self._queue_thread: threading.Thread = threading.Thread(
            target=self._process_queue,
        )
        self._lock: threading.Lock = threading.Lock()

    def _process_queue(self) -> None:
        """Events to process that are in the event queue."""
        try:
            while not self._done:
                try:
                    event = self._incoming_events.get(timeout=0.3)
                    self._process_event(event)
                except queue.Empty:
                    pass

            while not self._incoming_events.empty():
                event = self._incoming_events.get()
                self._process_event(event)
        except (OSError, RuntimeError) as e:
            LOGGER.exception("Error processing queue: %s", e)

    def _process_event(self, event: str) -> None:
        if self._server is not None:
            with self._lock:
                for client in self._server.clients:  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                    self._server.send_message(client, event)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                self._previous_events.append(event)

    def add_event(self, event: bytes) -> None:
        if self._done:
            error = "Can't add event, server already finished!"
            raise RuntimeError(error)
        encoded_event = base64.b64encode(event).decode("utf-8")
        self._incoming_events.put(encoded_event)

    def _on_open(self, client: dict[str, object], server: WebsocketServer) -> None:
        self._connected = True
        for event in self._previous_events:
            server.send_message(client, event)  # pyright: ignore[reportUnknownMemberType]

    def start(self) -> None:
        if not self._wait_for_client:
            return

        self._server = WebsocketServer(self._host, self._port)
        self._server.set_fn_new_client(self._on_open)  # pyright: ignore[reportUnknownMemberType]

        self._queue_thread.start()
        self._server.run_forever(threaded=True)

        while not self._connected:
            time.sleep(0.3)

    def shutdown_gracefully(self) -> None:
        if self._server is None:
            return
        self._server.keep_alive = False
        self._server._disconnect_clients_gracefully(1000, bytes("", encoding="utf-8"))  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001
        # These bottom two are flipped from regular order in websocket_server
        self._server.shutdown()
        self._server.server_close()

    def finish(self) -> None:
        if not self._wait_for_client:
            return
        self._done = True
        try:
            self._queue_thread.join()
            self.shutdown_gracefully()
        except (OSError, RuntimeError) as e:
            LOGGER.exception("Error shutting down server: %s", e)

    def set_wait_for_client(self) -> None:
        self._wait_for_client = True
