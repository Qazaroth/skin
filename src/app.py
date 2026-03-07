"""App Controller - orchestrates screens and API calls"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from api_client import APIClient, APIError
from gateway import Gateway
from screens import (
    show_welcome, show_login, show_register,
    ChatShell, _error, _success, _status,
    GREEN, RED, YELLOW, BLURPLE, MUTED, LIGHT_TEXT
)
import config


class SkinApp:
    def __init__(self, version: str = "0.1", base_url: str = "http://localhost:3000/api"):
        self.console  = Console()
        self.version  = version
        self.base_url = base_url
        self.api      = APIClient(base_url=base_url)

    def run(self):
        try:
            self._main_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self.console.clear()
            self.console.print(
                f"\n  [bold {BLURPLE}]Goodbye from Skin! 👋[/]\n"
            )

    def _main_loop(self):
        # Try silent auto-login from saved session
        self.console.print(f"\n  [dim]Checking saved session…[/]")
        user = self.api.try_auto_login()
        if user:
            uname = user.get("username", "")
            self.console.print(f"\n  Saved session found for [bold]{uname}[/].")
            choice = Prompt.ask(
                f"  [bold {BLURPLE}]Resume as @{uname}?[/] [dim](y = resume, n = go to login)[/]",
                console=self.console,
                default="y"
            ).strip().lower()
            if choice in ("y", "yes", ""):
                outcome = self._enter_chat(user)
                if outcome == "quit":
                    return
            else:
                # User wants a different account — clear the saved session
                self.api.logout()

        while True:
            choice = show_welcome(self.console, self.version)

            if choice == "quit":
                return

            elif choice == "login":
                result = self._do_login()
                if result == "quit":
                    return
                if result == "ok":
                    outcome = self._enter_chat()
                    if outcome == "quit":
                        return

            elif choice == "register":
                result = self._do_register()
                if result == "quit":
                    return
                if result == "ok":
                    outcome = self._enter_chat()
                    if outcome == "quit":
                        return

            elif choice == "config":
                self._do_config()

    # ── Config ────────────────────────────────────────────────────────────────

    def _do_config(self):
        self.console.print(f"\n  Current server: [bold]{self.base_url}[/]")
        new_url = Prompt.ask(
            f"  [bold {BLURPLE}]New server URL[/] (leave blank to cancel)",
            console=self.console,
            default=""
        ).strip()

        if not new_url:
            return

        if not new_url.startswith("http"):
            _error(self.console, "URL must start with http:// or https://")
            self.console.input("  Press Enter…")
            return

        self.base_url = new_url
        self.api = APIClient(base_url=new_url)
        cfg = config.load()
        cfg["base_url"] = new_url
        config.save(cfg)
        _success(self.console, f"Server updated to: {new_url}")
        self.console.input("  Press Enter…")

    # ── Auth flows ────────────────────────────────────────────────────────────

    def _do_login(self) -> str:
        """Returns 'ok', 'back', or 'quit'."""
        while True:
            creds = show_login(self.console, self.version)
            if creds is None:
                return "back"

            email, password = creds
            self.console.print(f"\n  [dim]Connecting…[/]")
            try:
                self.api.login(email, password)
                _success(self.console, "Logged in!")
                self.console.input("  Press Enter to continue…")
                return "ok"
            except APIError as e:
                _error(self.console, str(e))
                from rich.prompt import Confirm
                if not Confirm.ask("  [bold]Try again?[/]", console=self.console):
                    return "back"

    def _do_register(self) -> str:
        """Returns 'ok', 'back', or 'quit'."""
        while True:
            fields = show_register(self.console, self.version)
            if fields is None:
                return "back"

            username, email, password = fields
            self.console.print(f"\n  [dim]Creating account…[/]")
            try:
                self.api.register(username, email, password)
                # Register returns no token — login immediately after
                self.api.login(email, password)
                _success(self.console, f"Account created! Welcome, {username}!")
                self.console.input("  Press Enter to continue…")
                return "ok"
            except APIError as e:
                _error(self.console, str(e))
                if e.requirements:
                    for req in e.requirements:
                        self.console.print(f"    [dim]• {req}[/]")
                from rich.prompt import Confirm
                if not Confirm.ask("  [bold]Try again?[/]", console=self.console):
                    return "back"

    # ── Chat ──────────────────────────────────────────────────────────────────

    def _enter_chat(self, user: dict = None) -> str:
        """Fetch profile, launch chat shell. Returns 'logout' or 'quit'."""
        if user is None:
            try:
                user = self.api.get_me()
            except APIError as e:
                _error(self.console, f"Could not fetch profile: {e}")
                self.console.input("  Press Enter…")
                return "logout"

        # Derive WebSocket URL from the REST base URL
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = ws_url.rsplit("/api", 1)[0]  # strip /api suffix → ws://localhost:3000

        shell = ChatShell(self.console, self.api, user, self.version)

        # Pre-load DM channels and guilds so the sidebar is populated immediately
        try:
            shell.dm_channels = self.api.get_dm_channels()
        except Exception:
            pass
        try:
            shell.guilds = self.api.get_guilds()
        except Exception:
            pass

        def _refresh_token() -> bool:
            try:
                self.api._refresh_access_token()
                return True
            except Exception:
                return False

        gateway = Gateway(
            ws_url        = ws_url,
            get_token     = lambda: self.api.access_token or "",
            on_event      = shell.on_gateway_event,
            on_status     = shell.on_gateway_status,
            refresh_token = _refresh_token,
        )
        gateway.start()
        shell._gateway = gateway  # expose for TYPING_START sends

        result = shell.run()

        gateway.stop()

        if result == "logout":
            try:
                self.api.logout()
            except Exception:
                pass

        return result