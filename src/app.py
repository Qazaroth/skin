"""App Controller - orchestrates screens and API calls"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from api_client import APIClient, APIError
from src.screens import (
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
                _success(self.console, f"Account created! Welcome, {username}!")
                self.console.input("  Press Enter to continue…")
                return "ok"
            except APIError as e:
                _error(self.console, str(e))
                from rich.prompt import Confirm
                if not Confirm.ask("  [bold]Try again?[/]", console=self.console):
                    return "back"

    # ── Chat ──────────────────────────────────────────────────────────────────

    def _enter_chat(self) -> str:
        """Fetch profile, launch chat shell. Returns 'logout' or 'quit'."""
        try:
            user = self.api.get_me()
        except APIError as e:
            _error(self.console, f"Could not fetch profile: {e}")
            self.console.input("  Press Enter…")
            return "logout"

        shell  = ChatShell(self.console, self.api, user, self.version)
        result = shell.run()

        if result in ("logout", "quit"):
            try:
                self.api.logout()
            except Exception:
                pass

        return result