"""App Controller - orchestrates screens and API calls"""

from rich.console import Console
from api_client import APIClient, APIError
from screens import (
    show_welcome, show_login, show_register,
    ChatShell, _error, _success, _status,
    GREEN, RED, BLURPLE
)


class SkinApp:
    def __init__(self):
        self.console = Console()
        self.api     = APIClient()

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
            choice = show_welcome(self.console)

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
                    # "logout" → loop back to welcome

            elif choice == "register":
                result = self._do_register()
                if result == "quit":
                    return
                if result == "ok":
                    outcome = self._enter_chat()
                    if outcome == "quit":
                        return

    # ── Auth flows ────────────────────────────────────────────────────────────

    def _do_login(self) -> str:
        """Returns 'ok', 'back', or 'quit'."""
        while True:
            creds = show_login(self.console)
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
            fields = show_register(self.console)
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

        shell  = ChatShell(self.console, self.api, user)
        result = shell.run()   # "logout" or "quit"

        if result in ("logout", "quit"):
            try:
                self.api.logout()
            except Exception:
                pass

        return result