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

def _logo(version: str = "0.1") -> Panel:
    logo = Text(justify="center")
    logo.append("\n")
    logo.append("  ███████╗██╗  ██╗██╗███╗   ██╗\n", style=f"bold {BLURPLE}")
    logo.append("  ██╔════╝██║ ██╔╝██║████╗  ██║\n", style=f"bold {BLURPLE}")
    logo.append("  ███████╗█████╔╝ ██║██╔██╗ ██║\n", style=f"bold {BLURPLE}")
    logo.append("  ╚════██║██╔═██╗ ██║██║╚██╗██║\n", style=f"bold {BLURPLE}")
    logo.append("  ███████║██║  ██╗██║██║ ╚████║\n", style=f"bold {BLURPLE}")
    logo.append("  ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝\n", style=f"bold {BLURPLE}")
    logo.append(f"              Terminal Client  v{version}\n", style=f"dim {BLURPLE}")
    return Panel(logo, border_style=BLURPLE, box=box.DOUBLE_EDGE)


def _status(console: Console, msg: str, style: str = GREEN):
    console.print(f"  [bold {style}]▶[/]  {msg}")


def _error(console: Console, msg: str):
    console.print(Panel(f"[bold {RED}]✗  {msg}[/]", border_style=RED, padding=(0, 1)))


def _success(console: Console, msg: str):
    console.print(Panel(f"[bold {GREEN}]✓  {msg}[/]", border_style=GREEN, padding=(0, 1)))


# ── Welcome screen ────────────────────────────────────────────────────────────

def show_welcome(console: Console, version: str = "0.1") -> str:
    """Returns 'login', 'register', 'config', or 'quit'"""
    console.clear()
    console.print(_logo(version))
    console.print()

    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 3))
    table.add_column(justify="center")
    table.add_row(f"[bold {BLURPLE}][1][/]  Login")
    table.add_row(f"[bold {BLURPLE}][2][/]  Register")
    table.add_row(f"[bold {BLURPLE}][3][/]  Change Server")
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
        if choice in ("3", "server", "config"):
            return "config"
        if choice in ("q", "quit"):
            return "quit"
        _error(console, "Enter 1, 2, 3, or q")


# ── Login screen ──────────────────────────────────────────────────────────────

def show_login(console: Console, version: str = "0.1") -> tuple[str, str] | None:
    """Returns (login, password) or None if user cancels."""
    console.clear()
    console.print(_logo(version))
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

def show_register(console: Console, version: str = "0.1") -> tuple[str, str, str] | None:
    """Returns (username, email, password) or None if user cancels."""
    console.clear()
    console.print(_logo(version))
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

  [bold]/help[/]                    Show this message
  [bold]/me[/]                      Show your profile
  [bold]/edit <field> <val>[/]      Update profile  (fields: username, displayName, avatar_url)
  [bold]/dms[/]                     List your DM conversations
  [bold]/dm <username_or_id>[/]     Open a DM with a user by their ID
  [bold]/config[/]                  Show or change the server URL
  [bold]/logout[/]                  Log out
  [bold]/quit[/]                    Exit the client

[dim]── Coming soon ──────────────────────────────────────────[/dim]
  /join  /leave  /servers  (requires backend guild channels/WS)
"""

    EDITABLE_FIELDS = ("username", "displayName", "avatar_url")

    def __init__(self, console: Console, api_client, user: dict, version: str = "0.1"):
        self.console         = console
        self.api             = api_client
        self.user            = user
        self.version         = version
        self.messages        = []
        self.current_ch      = None
        self.current_ch_name = "home"
        self.dm_channels     = []
        self.gw_status       = "connecting…"   # shown in sidebar
        self.gw_ready        = False

    # ── Gateway callbacks (called from background thread) ─────────────────────

    def on_gateway_status(self, state: str, msg: str):
        self.gw_status = msg
        self.gw_ready  = (state == "ready")

    def on_gateway_event(self, op: str, data: dict):
        """Handle incoming gateway ops. Extend here as Phase 2 ops arrive."""
        if op == "READY":
            pass  # status already updated in on_gateway_status
        # Future: MESSAGE_CREATE, MESSAGE_UPDATE, MESSAGE_DELETE, PRESENCE_UPDATE…

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_header(self):
        uname = self.user.get("username", "unknown")
        left  = Text(f" ◈  Skin v{self.version}", style=f"bold {BLURPLE}")
        right = Text(f"@{uname} ● {self.current_ch_name} ", style=f"{MUTED}")
        rule  = Table.grid(expand=True)
        rule.add_column()
        rule.add_column(justify="right")
        rule.add_row(left, right)
        self.console.print(rule, style=f"on {DARK_BG}")
        self.console.print(Rule(style=BLURPLE))

    def _render_messages(self):
        if not self.messages:
            hint = "Select a DM with /dms or /dm <id>" if not self.current_ch else "No messages yet. Say something!"
            self.console.print(Align.center(f"\n[dim {MUTED}]{hint}[/]\n"))
            return
        for author, content, ts, edited in self.messages[-20:]:
            edited_tag = f" [dim {MUTED}](edited)[/]" if edited else ""
            self.console.print(
                f"[bold {BLURPLE}]{author}[/] [dim {MUTED}]{ts}[/]{edited_tag}\n  {content}\n"
            )

    def _render_sidebar_and_input(self):
        uname  = self.user.get("username", "?")
        email  = self.user.get("email", "")
        if self.gw_ready:
            status = f"[bold {GREEN}]● online[/]"
        else:
            status = f"[bold {YELLOW}]◌ {self.gw_status}[/]"

        dm_lines = ""
        if self.dm_channels:
            for ch in self.dm_channels[:8]:
                name    = ch.get("participant_display_name") or ch.get("participant_username", "?")
                ch_id   = ch.get("id", "")
                active  = "▶ " if ch_id == self.current_ch else "  "
                dm_lines += f"[dim]{active}{name}[/]\n"
        else:
            dm_lines = "[dim]  /dms to load[/]\n"

        sidebar = Panel(
            f"[bold {LIGHT_TEXT}]@{uname}[/]\n"
            f"[dim]{email}[/]\n\n"
            f"{status}\n\n"
            f"[dim {MUTED}]── DMs ──────[/]\n"
            f"{dm_lines}",
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
            _error(self.console, f"Usage: /edit <field> <value>  (fields: {', '.join(self.EDITABLE_FIELDS)})")
            self.console.input("  Press Enter…")
            return
        field, value = parts[1], " ".join(parts[2:])
        if field not in self.EDITABLE_FIELDS:
            _error(self.console, f"Unknown field '{field}'. Editable fields: {', '.join(self.EDITABLE_FIELDS)}")
            self.console.input("  Press Enter…")
            return
        try:
            self.user = self.api.update_me(**{field: value})
            _success(self.console, f"Updated {field}!")
        except Exception as e:
            _error(self.console, str(e))
        self.console.input("  Press Enter…")

    def _cmd_dms(self):
        try:
            self.dm_channels = self.api.get_dm_channels()
        except Exception as e:
            _error(self.console, str(e))
            self.console.input("  Press Enter…")
            return

        if not self.dm_channels:
            self.console.print(f"  [dim {MUTED}]No DM conversations yet.[/]")
            self.console.input("  Press Enter…")
            return

        t = Table(title="DM Channels", box=box.ROUNDED, border_style=BLURPLE)
        t.add_column("#",          style=f"dim {MUTED}",    width=4)
        t.add_column("User",       style=f"bold {LIGHT_TEXT}")
        t.add_column("Channel ID", style=f"dim {MUTED}")

        for i, ch in enumerate(self.dm_channels, 1):
            name = ch.get("participant_display_name") or ch.get("participant_username", "?")
            t.add_row(str(i), name, ch.get("id", ""))

        self.console.print(t)
        self.console.print(f"  [dim {MUTED}]Use /dm <channel_id> to open a conversation.[/]")
        self.console.input("  Press Enter…")

    def _cmd_dm(self, parts: list[str]):
        if len(parts) < 2:
            _error(self.console, "Usage: /dm <recipient_id>")
            self.console.input("  Press Enter…")
            return

        recipient_id = parts[1]
        try:
            channel = self.api.open_dm(recipient_id)
        except Exception as e:
            _error(self.console, str(e))
            self.console.input("  Press Enter…")
            return

        ch_id   = channel.get("id")
        recip   = channel.get("recipient", {})
        name    = recip.get("displayName") or recip.get("username", recipient_id)

        self.current_ch      = ch_id
        self.current_ch_name = f"DM:{name}"
        self.messages        = []

        # Load message history
        try:
            history = self.api.get_messages(ch_id, limit=50)
            for msg in reversed(history):
                author  = msg.get("author_display_name") or msg.get("author_username", "?")
                content = msg.get("content", "")
                ts      = self._fmt_ts(msg.get("created_at"))
                edited  = bool(msg.get("edited_at"))
                self.messages.append((author, content, ts, edited))
        except Exception:
            pass

    def _fmt_ts(self, ts_raw) -> str:
        import datetime
        try:
            ts = int(ts_raw)
            if ts <= 0:
                raise ValueError
            ts = ts / 1000 if ts > 1e10 else ts
            return datetime.datetime.fromtimestamp(ts).astimezone().strftime("%H:%M")
        except (ValueError, TypeError, OSError):
            return datetime.datetime.now().strftime("%H:%M")

    def _cmd_send(self, text: str):
        """Send a message to the current channel via REST."""
        if not self.current_ch:
            _error(self.console, "No channel selected. Use /dms or /dm <username> first.")
            self.console.input("  Press Enter…")
            return
        try:
            msg     = self.api.send_message(self.current_ch, text)
            author  = msg.get("author_display_name") or msg.get("author_username", "?")
            content = msg.get("content", text)
            ts      = self._fmt_ts(msg.get("created_at"))
            self.messages.append((author, content, ts, False))
        except Exception as e:
            _error(self.console, str(e))
            self.console.input("  Press Enter…")

    def _read_input(self) -> str | None:
        """
        Read a line of input, but wake up every second to check for
        gateway status changes and re-render if needed.
        Returns the input string, or None on KeyboardInterrupt.
        """
        import sys
        import select

        prompt = f"  \x1b[1;34m{self.current_ch_name} >\x1b[0m "
        sys.stdout.write(prompt)
        sys.stdout.flush()

        buf = ""
        last_status = self.gw_status

        while True:
            # Check if stdin has data, with a 1-second timeout
            try:
                ready, _, _ = select.select([sys.stdin], [], [], 1.0)
            except (ValueError, OSError):
                # stdin closed or unavailable (e.g. Windows — fall back)
                try:
                    return input()
                except KeyboardInterrupt:
                    return None

            if ready:
                try:
                    char = sys.stdin.read(1)
                except KeyboardInterrupt:
                    return None
                if char in ("\n", "\r"):
                    sys.stdout.write("\n")
                    return buf.strip()
                elif char in ("\x7f", "\x08"):  # backspace
                    if buf:
                        buf = buf[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif char == "\x03":  # Ctrl+C
                    return None
                else:
                    buf += char
                    sys.stdout.write(char)
                    sys.stdout.flush()
            else:
                # Timeout — check if gateway status changed
                if self.gw_status != last_status:
                    last_status = self.gw_status
                    # Re-render: clear line, redraw screen, reprint prompt + buffer
                    sys.stdout.write("\r\x1b[2K")
                    sys.stdout.flush()
                    self._full_render()
                    sys.stdout.write(prompt + buf)
                    sys.stdout.flush()

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self) -> str:
        """Run the chat shell. Returns 'logout' or 'quit'."""
        self._full_render()
        while True:
            try:
                raw = self._read_input()
            except KeyboardInterrupt:
                raw = None

            if raw is None:
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

                elif cmd == "/dms":
                    self._cmd_dms()

                elif cmd == "/dm":
                    self._cmd_dm(parts)

                elif cmd == "/config":
                    self.console.print(f"\n  Current server: [bold]{self.api.base_url}[/]")
                    new_url = Prompt.ask(
                        f"  [bold {BLURPLE}]New server URL[/] (leave blank to cancel)",
                        console=self.console,
                        default=""
                    ).strip()
                    if new_url:
                        if not new_url.startswith("http"):
                            _error(self.console, "URL must start with http:// or https://")
                        else:
                            self.api.base_url = new_url
                            import config as _config
                            cfg = _config.load()
                            cfg["base_url"] = new_url
                            _config.save(cfg)
                            _success(self.console, f"Server updated to: {new_url}")
                    self.console.input("  Press Enter…")

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
                self._cmd_send(raw)

            self._full_render()