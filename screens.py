"""TUI Screens - Rich-based UI components for Skin"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.style import Style
from rich.rule import Rule
from rich import box
from rich.layout import Layout
from rich.live import Live
import getpass

# ── Colour palette ────────────────────────────────────────────────────────────
BLURPLE   = "#5865F2"
GREEN     = "#57F287"
RED       = "#ED4245"
YELLOW    = "#FEE75C"
DARK_BG   = "#2B2D31"
MID_BG    = "#313338"
LIGHT_TEXT = "#DBDEE1"
MUTED     = "#949BA4"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _logo() -> Panel:
    logo = Text(justify="center")
    logo.append("\n")
    logo.append("  ███████╗██╗  ██╗██╗███╗   ██╗\n", style=f"bold {BLURPLE}")
    logo.append("  ██╔════╝██║ ██╔╝██║████╗  ██║\n", style=f"bold {BLURPLE}")
    logo.append("  ███████╗█████╔╝ ██║██╔██╗ ██║\n", style=f"bold {BLURPLE}")
    logo.append("  ╚════██║██╔═██╗ ██║██║╚██╗██║\n", style=f"bold {BLURPLE}")
    logo.append("  ███████║██║  ██╗██║██║ ╚████║\n", style=f"bold {BLURPLE}")
    logo.append("  ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝\n", style=f"bold {BLURPLE}")
    logo.append("              Terminal Client  v0.1\n", style=f"dim {BLURPLE}")
    return Panel(logo, border_style=BLURPLE, box=box.DOUBLE_EDGE)


def _status(console: Console, msg: str, style: str = GREEN):
    console.print(f"  [bold {style}]▶[/]  {msg}")


def _error(console: Console, msg: str):
    console.print(Panel(f"[bold {RED}]✗  {msg}[/]", border_style=RED, padding=(0, 1)))


def _success(console: Console, msg: str):
    console.print(Panel(f"[bold {GREEN}]✓  {msg}[/]", border_style=GREEN, padding=(0, 1)))


# ── Welcome screen ────────────────────────────────────────────────────────────

def show_welcome(console: Console) -> str:
    """Returns 'login', 'register', or 'quit'"""
    console.clear()
    console.print(_logo())
    console.print()

    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 3))
    table.add_column(justify="center")
    table.add_row(f"[bold {BLURPLE}][1][/]  Login")
    table.add_row(f"[bold {BLURPLE}][2][/]  Register")
    table.add_row(f"[bold {MUTED}][q][/]  Quit")

    console.print(Align.center(table))
    console.print()

    while True:
        choice = Prompt.ask(
            f"  [bold {BLURPLE}]>[/] Choose",
            console=console,
            default="1"
        ).strip().lower()

        if choice in ("1", "login"):
            return "login"
        if choice in ("2", "register"):
            return "register"
        if choice in ("q", "quit"):
            return "quit"
        _error(console, "Enter 1, 2, or q")


# ── Login screen ──────────────────────────────────────────────────────────────

def show_login(console: Console) -> tuple[str, str] | None:
    """Returns (login, password) or None if user cancels."""
    console.clear()
    console.print(_logo())
    console.print(
        Panel(f"[bold {BLURPLE}]Login[/]  — press Ctrl+C to go back",
              border_style=BLURPLE, padding=(0, 1))
    )
    console.print()
    try:
        login    = Prompt.ask(f"  [bold {BLURPLE}]Username or Email[/]", console=console)
        password = getpass.getpass("  Password: ")
        return login.strip(), password
    except KeyboardInterrupt:
        return None


# ── Register screen ───────────────────────────────────────────────────────────

def show_register(console: Console) -> tuple[str, str, str] | None:
    """Returns (username, email, password) or None if user cancels."""
    console.clear()
    console.print(_logo())
    console.print(
        Panel(f"[bold {BLURPLE}]Create Account[/]  — press Ctrl+C to go back",
              border_style=BLURPLE, padding=(0, 1))
    )
    console.print()
    try:
        username = Prompt.ask(f"  [bold {BLURPLE}]Username[/]", console=console)
        email    = Prompt.ask(f"  [bold {BLURPLE}]Email   [/]", console=console)
        password = getpass.getpass("  Password: ")
        confirm  = getpass.getpass("  Confirm : ")
        if password != confirm:
            _error(console, "Passwords do not match.")
            console.input("  Press Enter to try again…")
            return None
        return username.strip(), email.strip(), password
    except KeyboardInterrupt:
        return None


# ── Main chat shell ───────────────────────────────────────────────────────────

class ChatShell:
    """
    Interactive shell shown after login.
    Renders a sidebar + message area using Rich.
    WebSocket integration and real channels/DMs will plug in here.
    """

    HELP_TEXT = f"""
[bold {BLURPLE}]Available commands[/]

  [bold]/help[/]               Show this message
  [bold]/me[/]                 Show your profile
  [bold]/edit <field> <val>[/] Update your profile  (e.g. /edit username Joe)
  [bold]/logout[/]             Log out
  [bold]/quit[/]               Exit the client

[dim]── Coming soon ──────────────────────────────────────────[/dim]
  /join  /leave  /dm  /servers  (requires backend channels/WS)
"""

    def __init__(self, console: Console, api_client, user: dict):
        self.console    = console
        self.api        = api_client
        self.user       = user
        self.messages   = []          # list of (author, content) tuples
        self.current_ch = "#general"  # placeholder

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_header(self):
        uname = self.user.get("username", "unknown")
        left  = Text(f" ◈  Skin", style=f"bold {BLURPLE}")
        right = Text(f"@{uname} ● {self.current_ch} ", style=f"{MUTED}")
        rule  = Table.grid(expand=True)
        rule.add_column()
        rule.add_column(justify="right")
        rule.add_row(left, right)
        self.console.print(rule, style=f"on {DARK_BG}")
        self.console.print(Rule(style=BLURPLE))

    def _render_messages(self):
        if not self.messages:
            self.console.print(
                Align.center(
                    f"\n[dim {MUTED}]No messages yet. Say something![/]\n"
                )
            )
            return
        for author, content, ts in self.messages[-20:]:
            self.console.print(
                f"[bold {BLURPLE}]{author}[/] [dim {MUTED}]{ts}[/]\n  {content}\n"
            )

    def _render_sidebar_and_input(self):
        uname  = self.user.get("username", "?")
        email  = self.user.get("email", "")
        status = f"[bold {GREEN}]● online[/]"

        sidebar = Panel(
            f"[bold {LIGHT_TEXT}]@{uname}[/]\n"
            f"[dim]{email}[/]\n\n"
            f"{status}\n\n"
            f"[dim {MUTED}]── Servers ──[/]\n"
            f"[dim]  (none yet)[/]\n\n"
            f"[dim {MUTED}]── DMs ──────[/]\n"
            f"[dim]  (none yet)[/]",
            title=f"[bold {BLURPLE}]You[/]",
            border_style=BLURPLE,
            width=28,
        )
        hint = Panel(
            f"[dim {MUTED}]Type a message or /help for commands[/]",
            border_style=DARK_BG,
            padding=(0, 1),
        )
        self.console.print(Columns([sidebar, hint], expand=True))

    def _full_render(self):
        self.console.clear()
        self._render_header()
        self._render_messages()
        self._render_sidebar_and_input()

    # ── Command handling ──────────────────────────────────────────────────────

    def _cmd_me(self):
        try:
            self.user = self.api.get_me()
        except Exception as e:
            _error(self.console, str(e))
            return

        import datetime
        TIMESTAMP_FIELDS = {"created_at", "updated_at", "deleted_at"}

        def fmt_value(k, v):
            if k.lower() in TIMESTAMP_FIELDS and v is not None:
                try:
                    ts = int(v) / 1000 if int(v) > 1e10 else int(v)
                    dt = datetime.datetime.fromtimestamp(ts).astimezone()
                    return dt.strftime("%d %b %Y, %H:%M %Z")
                except (ValueError, TypeError, OSError):
                    pass
            return str(v)

        t = Table(title="Your Profile", box=box.ROUNDED, border_style=BLURPLE)
        t.add_column("Field",  style=f"bold {BLURPLE}")
        t.add_column("Value",  style=LIGHT_TEXT)
        for k, v in self.user.items():
            if k.lower() not in ("password", "passwordhash"):
                t.add_row(str(k), fmt_value(k, v))
        self.console.print(t)
        self.console.input(f"\n  [dim]Press Enter to continue…[/dim]")

    def _cmd_edit(self, parts: list[str]):
        if len(parts) < 3:
            _error(self.console, "Usage: /edit <field> <value>")
            self.console.input("  Press Enter…")
            return
        field, value = parts[1], " ".join(parts[2:])
        try:
            self.user = self.api.update_me(**{field: value})
            _success(self.console, f"Updated {field}!")
        except Exception as e:
            _error(self.console, str(e))
        self.console.input("  Press Enter…")

    def _fake_send(self, text: str):
        """Placeholder until WebSocket messages are wired up."""
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M")
        uname = self.user.get("username", "me")
        self.messages.append((uname, text, ts))

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self) -> str:
        """Run the chat shell. Returns 'logout' or 'quit'."""
        self._full_render()
        while True:
            try:
                raw = self.console.input(
                    f"  [bold {BLURPLE}]{self.current_ch} >[/] "
                ).strip()
            except KeyboardInterrupt:
                raw = "/logout"

            if not raw:
                continue

            if raw.startswith("/"):
                parts = raw.split()
                cmd   = parts[0].lower()

                if cmd == "/help":
                    self.console.print(Panel(self.HELP_TEXT, border_style=BLURPLE))
                    self.console.input("  Press Enter to continue…")

                elif cmd == "/me":
                    self._cmd_me()

                elif cmd == "/edit":
                    self._cmd_edit(parts)

                elif cmd == "/logout":
                    if Confirm.ask(f"  [bold {YELLOW}]Log out?[/]", console=self.console):
                        return "logout"

                elif cmd == "/quit":
                    if Confirm.ask(f"  [bold {RED}]Quit?[/]", console=self.console):
                        return "quit"

                else:
                    _error(self.console, f"Unknown command: {cmd}. Try /help")
                    self.console.input("  Press Enter…")
            else:
                self._fake_send(raw)

            self._full_render()