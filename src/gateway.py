"""WebSocket Gateway - Handles real-time connection to the Skeleton backend"""

import json
import threading
import time
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

# Close codes from the client guide
CLOSE_RECONNECT     = {4001, 4002, 4003}   # reconnect, fix client bug
CLOSE_TOKEN_EXPIRED = 4005                  # refresh token then reconnect
CLOSE_INVALID_TOKEN = 4006                  # must log in again
CLOSE_REPLACED      = 4004                  # another session took over


class GatewayState:
    DISCONNECTED = "disconnected"
    CONNECTING   = "connecting"
    IDENTIFYING  = "identifying"
    READY        = "ready"
    RECONNECTING = "reconnecting"


class Gateway:
    """
    Manages the WebSocket connection to the Skeleton gateway.

    Usage:
        gw = Gateway(ws_url, get_token_fn, on_event_fn, on_status_fn)
        gw.start()
        ...
        gw.stop()

    Callbacks:
        get_token()            → str   — called each time a fresh token is needed
        on_event(op, data)             — called for every server-sent op
        on_status(state, msg)          — called when connection state changes
    """

    WS_URL = "ws://localhost:3000"

    def __init__(
        self,
        ws_url:    str,
        get_token: Callable[[], str],
        on_event:  Callable[[str, dict], None],
        on_status: Callable[[str, str], None],
    ):
        self.ws_url    = ws_url
        self.get_token = get_token
        self.on_event  = on_event
        self.on_status = on_status

        self._ws          = None
        self._thread      = None
        self._stop_event  = threading.Event()
        self.state        = GatewayState.DISCONNECTED

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        """Start the gateway in a background thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Disconnect and stop the background thread."""
        self._stop_event.set()
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
        self.state = GatewayState.DISCONNECTED
        self.on_status(GatewayState.DISCONNECTED, "Disconnected.")

    # ── Internal loop ─────────────────────────────────────────────────────────

    def _run_loop(self):
        """Main reconnect loop with exponential backoff."""
        delay = 2
        while not self._stop_event.is_set():
            try:
                self._connect()
                delay = 2  # reset backoff on clean exit
            except Exception as e:
                if self._stop_event.is_set():
                    break
                self.state = GatewayState.RECONNECTING
                self.on_status(GatewayState.RECONNECTING, f"Reconnecting in {delay}s…")
                self._stop_event.wait(delay)
                delay = min(delay * 2, 60)

    def _connect(self):
        try:
            import websocket
        except ImportError:
            self.on_status(GatewayState.DISCONNECTED,
                           "websocket-client not installed. Run: pip install websocket-client")
            self._stop_event.set()
            return

        self.state = GatewayState.CONNECTING
        self.on_status(GatewayState.CONNECTING, "Connecting to gateway…")

        # No recv timeout — connection is long-lived and idle between events
        ws = websocket.create_connection(self.ws_url, timeout=None)
        self._ws = ws

        # Send IDENTIFY immediately
        self.state = GatewayState.IDENTIFYING
        self._send(ws, {"op": "IDENTIFY", "token": self.get_token()})
        self.on_status(GatewayState.IDENTIFYING, "Identifying…")

        disconnected_cleanly = False

        # Listen for messages
        while not self._stop_event.is_set():
            try:
                raw = ws.recv()
                if raw is None or raw == "":
                    # Server closed connection
                    disconnected_cleanly = True
                    break
            except Exception:
                break

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            op   = msg.get("op", "")
            data = msg.get("data", {})

            if op == "READY":
                self.state = GatewayState.READY
                uname = data.get("username", "")
                self.on_status(GatewayState.READY, f"Gateway ready — @{uname}")
                self.on_event(op, data)
            else:
                self.on_event(op, data)

        # Check close code for reconnect strategy
        try:
            code = ws.getstatus()
        except Exception:
            code = None

        self._ws = None

        # If we were asked to stop, exit cleanly with no reconnect
        if self._stop_event.is_set():
            return

        if code == CLOSE_TOKEN_EXPIRED:
            self.on_status(GatewayState.RECONNECTING, "Token expired — refreshing…")
        elif code == CLOSE_INVALID_TOKEN:
            self.on_status(GatewayState.DISCONNECTED, "Invalid token — please log in again.")
            self._stop_event.set()
            return
        elif code == CLOSE_REPLACED:
            self.on_status(GatewayState.DISCONNECTED, "Session replaced by another connection.")
            self._stop_event.set()
            return

        # Raise to trigger backoff reconnect in _run_loop
        raise ConnectionError(f"Gateway closed (code={code})")

    def _send(self, ws, payload: dict):
        ws.send(json.dumps(payload))