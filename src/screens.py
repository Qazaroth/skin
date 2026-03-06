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

  [bold]/help[/]                         Show this message
  [bold]/me[/]                           Show your profile
  [bold]/edit <field> <val>[/]           Update profile  (fields: username, displayName, avatar_url)
  [bold]/dms[/]                          List your DM conversations
  [bold]/dm <username>[/]                Open a DM with a user
  [bold]/mute [username][/]              Toggle mute on current or named channel
  [bold]/msgs[/]                         Show messages with index numbers
  [bold]/editmsg <#> <new content>[/]    Edit one of your messages by index
  [bold]/delmsg <#>[/]                   Delete one of your messages by index
  [bold]/config[/]                       Show or change the server URL
  [bold]/logout[/]                       Log out
  [bold]/quit[/]                         Exit the client

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
        self.message_ids     = []          # parallel list tracking message IDs for UPDATE/DELETE
        self.current_ch      = None
        self.current_ch_name = "home"
        self.dm_channels     = []
        self.gw_status       = "connecting…"   # shown in sidebar
        self.gw_ready        = False
        self._pending_render = False            # set by background thread to trigger re-render
        self.unread          = set()            # channel ids with unread messages
        self.muted           = set()            # channel ids with toasts suppressed
        self.notifications   = []              # list of (text, expires_at) toast messages

    # ── Gateway callbacks (called from background thread) ─────────────────────

    def on_gateway_status(self, state: str, msg: str):
        self.gw_status       = msg
        self.gw_ready        = (state == "ready")
        self._pending_render = True

    def on_gateway_event(self, op: str, data: dict):
        """Handle incoming gateway ops."""
        if op == "READY":
            pass  # status already handled in on_gateway_status

        elif op == "MESSAGE_CREATE":
            ch_id   = data.get("channel_id")
            author  = data.get("author_display_name") or data.get("author_username", "?")
            content = data.get("content", "")
            ts      = self._fmt_ts(data.get("created_at"))
            edited  = bool(data.get("edited_at"))

            if ch_id == self.current_ch:
                # Message is for the open channel — append directly
                self.messages.append((author, content, ts, edited))
                self.message_ids.append(data.get("id"))
                self._pending_render = True

            else:
                # Message is for a different (or unopened) channel
                # Refresh DM list if this channel isn't known yet
                if not any(ch.get("id") == ch_id for ch in self.dm_channels):
                    try:
                        self.dm_channels = self.api.get_dm_channels()
                    except Exception:
                        pass
                # Find the channel name for the notification
                ch_info   = next((c for c in self.dm_channels if c.get("id") == ch_id), {})
                ch_name   = self._fmt_participant(
                    ch_info.get("participant_display_name"),
                    ch_info.get("participant_username") or author
                )
                if ch_id not in self.muted:
                    preview = content if len(content) <= 40 else content[:37] + "…"
                    self._push_notification(f"DM from {ch_name}: {preview}  [dim](use /dm {ch_info.get('participant_username', ch_id)})[/]")
                self.unread.add(ch_id)
                self._pending_render = True

        elif op == "MESSAGE_UPDATE":
            ch_id = data.get("channel_id")
            if ch_id == self.current_ch:
                msg_id  = data.get("id")
                content = data.get("content", "")
                ts      = self._fmt_ts(data.get("created_at"))
                edited  = bool(data.get("edited_at"))
                author  = data.get("author_display_name") or data.get("author_username", "?")
                for i, (a, c, t, e) in enumerate(self.messages):
                    if self.message_ids[i] == msg_id:
                        self.messages[i] = (author, content, ts, True)
                        break
                self._pending_render = True

        elif op == "MESSAGE_DELETE":
            ch_id  = data.get("channel_id")
            msg_id = data.get("id")
            if ch_id == self.current_ch and msg_id in self.message_ids:
                idx = self.message_ids.index(msg_id)
                self.messages.pop(idx)
                self.message_ids.pop(idx)
                self._pending_render = True

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

    def _resolve_msg_index(self, raw: str):
        """
        Parse a 1-based message index from the user and return (list_index, message_id).
        Returns (None, None) and prints an error if invalid.
        """
        try:
            n = int(raw.lstrip("#"))
        except ValueError:
            _error(self.console, f"'{raw}' is not a valid message number.")
            return None, None
        if n < 1 or n > len(self.messages):
            _error(self.console, f"No message #{n}. You have {len(self.messages)} messages loaded.")
            return None, None
        idx    = n - 1
        msg_id = self.message_ids[idx] if idx < len(self.message_ids) else None
        if not msg_id:
            _error(self.console, f"Message #{n} has no ID — it may have been loaded before tracking began. Use /dm to reload.")
            return None, None
        return idx, msg_id

    def _cmd_editmsg(self, parts: list[str]):
        if len(parts) < 3:
            _error(self.console, "Usage: /editmsg <#> <new content>")
            self.console.input("  Press Enter…")
            return
        if not self.current_ch:
            _error(self.console, "No channel open.")
            self.console.input("  Press Enter…")
            return
        idx, msg_id = self._resolve_msg_index(parts[1])
        if msg_id is None:
            self.console.input("  Press Enter…")
            return
        new_content = " ".join(parts[2:])
        try:
            self.api.edit_message(self.current_ch, msg_id, new_content)
            # Gateway MESSAGE_UPDATE will update the display automatically
        except Exception as e:
            _error(self.console, str(e))
            self.console.input("  Press Enter…")

    def _cmd_delmsg(self, parts: list[str]):
        if len(parts) < 2:
            _error(self.console, "Usage: /delmsg <#>")
            self.console.input("  Press Enter…")
            return
        if not self.current_ch:
            _error(self.console, "No channel open.")
            self.console.input("  Press Enter…")
            return
        idx, msg_id = self._resolve_msg_index(parts[1])
        if msg_id is None:
            self.console.input("  Press Enter…")
            return
        try:
            self.api.delete_message(self.current_ch, msg_id)
            # Gateway MESSAGE_DELETE will remove it from display automatically
        except Exception as e:
            _error(self.console, str(e))
            self.console.input("  Press Enter…")

    def _cmd_mute(self, parts: list[str]):
        """Toggle mute for the current channel or a named one."""
        # If a username arg is given, find that channel; otherwise use current
        if len(parts) >= 2:
            target_username = parts[1]
            ch = next((
                c for c in self.dm_channels
                if c.get("participant_username", "").lower() == target_username.lower()
            ), None)
            if not ch:
                _error(self.console, f"No DM channel found for '{target_username}'. Use /dms to list channels.")
                self.console.input("  Press Enter…")
                return
            ch_id   = ch.get("id")
            ch_name = self._fmt_participant(ch.get("participant_display_name"), ch.get("participant_username"))
        elif self.current_ch:
            ch_id   = self.current_ch
            ch_name = self.current_ch_name
        else:
            _error(self.console, "No channel open. Use /mute <username> or open a DM first.")
            self.console.input("  Press Enter…")
            return

        if ch_id in self.muted:
            self.muted.discard(ch_id)
            _success(self.console, f"Unmuted {ch_name}.")
        else:
            self.muted.add(ch_id)
            _success(self.console, f"Muted {ch_name}. You'll still see unread dots but no toasts.")
        self.console.input("  Press Enter…")

    def _push_notification(self, text: str, duration: float = 8.0):
        """Add a toast notification that expires after `duration` seconds."""
        import time
        self.notifications.append((text, time.monotonic() + duration))

    def _render_messages(self):
        import time
        # Expire old notifications
        now = time.monotonic()
        self.notifications = [(t, exp) for t, exp in self.notifications if exp > now]
        # Show active notifications as a toast bar
        for text, _ in self.notifications:
            self.console.print(Panel(
                f"[bold {YELLOW}]🔔 {text}[/]",
                border_style=YELLOW,
                padding=(0, 1),
            ))

        if not self.messages:
            hint = "Select a DM with /dms or /dm <username>" if not self.current_ch else "No messages yet. Say something!"
            self.console.print(Align.center(f"\n[dim {MUTED}]{hint}[/]\n"))
            return
        visible = self.messages[-20:]
        offset  = len(self.messages) - len(visible)  # so #1 is always the oldest shown
        for i, (author, content, ts, edited) in enumerate(visible, start=offset + 1):
            edited_tag = f" [dim {MUTED}](edited)[/]" if edited else ""
            idx_tag    = f"[dim {MUTED}]#{i}[/] "
            self.console.print(
                f"{idx_tag}[bold {BLURPLE}]{author}[/] [dim {MUTED}]{ts}[/]{edited_tag}\n  {content}\n"
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
                name    = self._fmt_participant(ch.get("participant_display_name"), ch.get("participant_username"))
                ch_id   = ch.get("id", "")
                active  = "▶ " if ch_id == self.current_ch else "  "
                unread  = f"[bold {GREEN}] ●[/]" if ch_id in self.unread else ""
                muted   = f" [dim {MUTED}]🔇[/]" if ch_id in self.muted else ""
                dm_lines += f"[dim]{active}{name}[/]{unread}{muted}\n"
        else:
            dm_lines = "[dim]  (none yet)[/]\n"

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
            name = self._fmt_participant(ch.get("participant_display_name"), ch.get("participant_username"))
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
        name    = self._fmt_participant(recip.get("displayName"), recip.get("username", recipient_id))

        self.current_ch      = ch_id
        self.current_ch_name = f"DM:{name}"
        self.messages        = []
        self.message_ids     = []
        self.unread.discard(ch_id)

        # Load message history
        try:
            history = self.api.get_messages(ch_id, limit=50)
            for msg in reversed(history):
                author  = msg.get("author_display_name") or msg.get("author_username", "?")
                content = msg.get("content", "")
                ts      = self._fmt_ts(msg.get("created_at"))
                edited  = bool(msg.get("edited_at"))
                self.messages.append((author, content, ts, edited))
                self.message_ids.append(msg.get("id"))
        except Exception:
            pass

    def _fmt_participant(self, display_name, username) -> str:
        """Format as 'Display Name (username)' or just 'username' if no display name."""
        if display_name and display_name != username:
            return f"{display_name} ({username})"
        return username or "?"

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
            self.api.send_message(self.current_ch, text)
            # Do NOT append locally — MESSAGE_CREATE from the gateway will handle display
        except Exception as e:
            _error(self.console, str(e))
            self.console.input("  Press Enter…")

    def _read_input(self) -> str | None:
        """
        Read a line of input non-blocking on both Windows and Linux/Mac.
        Uses a background thread for stdin so the main thread can poll for
        gateway updates and re-render every 0.1s without waiting for Enter.
        """
        import sys
        import threading

        prompt = f"  \x1b[1;34m{self.current_ch_name} >\x1b[0m "
        sys.stdout.write(prompt)
        sys.stdout.flush()

        result_holder = [None]       # [0] = result string, or None if interrupted
        done          = threading.Event()

        def _reader():
            try:
                result_holder[0] = input()
            except (EOFError, KeyboardInterrupt):
                result_holder[0] = None
            finally:
                done.set()

        t = threading.Thread(target=_reader, daemon=True)
        t.start()

        while not done.wait(timeout=0.1):
            import time
            now = time.monotonic()
            has_expiring = any(exp <= now for _, exp in self.notifications)
            if self._pending_render or has_expiring:
                self._pending_render = False
                # Clear current line, re-render, reprint prompt
                # We can't show the typed buffer since input() owns stdin,
                # but we can at least keep the screen fresh
                sys.stdout.write("\r\x1b[2K")
                sys.stdout.flush()
                self._full_render()
                sys.stdout.write(prompt)
                sys.stdout.flush()

        return result_holder[0]

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

                elif cmd == "/mute":
                    self._cmd_mute(parts)

                elif cmd == "/msgs":
                    self._full_render()

                elif cmd == "/editmsg":
                    self._cmd_editmsg(parts)

                elif cmd == "/delmsg":
                    self._cmd_delmsg(parts)

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