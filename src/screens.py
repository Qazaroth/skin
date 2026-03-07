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
import sys

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
  [bold]/avatar <path>[/]                Upload a new avatar image (JPEG, PNG, GIF, WebP — max 8MB)
  [bold]/dms[/]                          List your DM conversations
  [bold]/dm <username>[/]                Open or resume a DM with a user (use their username, not ID)
  [bold]/guild[/]                        List all guilds you are in
  [bold]/guild <name or #>[/]            View guild channels & members — pick a number to join
  [bold]/guild create <n>[/]          Create a new guild
  [bold]/joinserver <guild_id>[/]        Join a guild by ID
  [bold]/mute [username][/]              Toggle mute on current or named channel
  [bold]/msgs[/]                         Show messages with index numbers
  [bold]/editmsg <#> <new content>[/]    Edit one of your messages by index
  [bold]/delmsg <#>[/]                   Delete one of your messages by index
  [bold]/config[/]                       Show or change the server URL
  [bold]/logout[/]                       Log out
  [bold]/quit[/]                         Exit the client

[dim]── Coming soon ──────────────────────────────────────────────────────[/dim]
  /leave, voice channels  (not yet in backend)
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
        self.guilds          = []          # list of guild summaries from GET /users/@me/guilds
        self.current_guild_id = None       # id of the guild whose channel is currently open
        self.channel_guild_map = {}        # channel_id → guild_id, populated when viewing a guild
        self.channel_name_map  = {}        # channel_id → channel name, for /join by name
        self.presence_map      = {}        # user_id → "online" | "offline"
        self.typing_users      = {}        # channel_id → {username: expires_at}
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
                pid_t, uname_t, dname_t = self._resolve_dm_participant(ch_info)
                ch_name = self._fmt_participant(dname_t, uname_t or author)
                if ch_id not in self.muted:
                    preview = content if len(content) <= 40 else content[:37] + "…"
                    dm_cmd = uname_t or author
                    self._push_notification(f"DM from {ch_name}: {preview}  [dim](use /dm {dm_cmd})[/]")
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

        elif op == "PRESENCE_UPDATE":
            user_id = data.get("userId")
            status  = data.get("status", "offline")
            if user_id:
                self.presence_map[user_id] = status
                self._pending_render = True

        elif op == "TYPING_START":
            import time
            ch_id    = data.get("channelId")
            username = data.get("username", "?")
            user_id  = data.get("userId")
            # Only show if it's in the current channel and not ourselves
            my_id = self.user.get("id")
            if ch_id == self.current_ch and user_id != my_id:
                if ch_id not in self.typing_users:
                    self.typing_users[ch_id] = {}
                self.typing_users[ch_id][username] = time.monotonic() + 3.0
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
                if self._resolve_dm_participant(c)[1] and
                   self._resolve_dm_participant(c)[1].lower() == target_username.lower()
            ), None)
            if not ch:
                _error(self.console, f"No DM channel found for '{target_username}'. Use /dms to list channels.")
                self.console.input("  Press Enter…")
                return
            ch_id   = ch.get("id")
            _, uname_m, dname_m = self._resolve_dm_participant(ch)
            ch_name = self._fmt_participant(dname_m, uname_m)
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

        # Typing indicator — expire stale entries then show active ones
        if self.current_ch and self.current_ch in self.typing_users:
            self.typing_users[self.current_ch] = {
                u: exp for u, exp in self.typing_users[self.current_ch].items() if exp > now
            }
            typers = list(self.typing_users[self.current_ch].keys())
            if typers:
                names = ", ".join(typers)
                verb  = "is" if len(typers) == 1 else "are"
                self.console.print(f"  [dim {MUTED}]• {names} {verb} typing…[/]")

    def _render_sidebar_and_input(self):
        uname  = self.user.get("username", "?")
        email  = self.user.get("email", "")
        if self.gw_ready:
            status = f"[bold {GREEN}]● online[/]"
        else:
            status = f"[bold {YELLOW}]◌ {self.gw_status}[/]"

        dm_lines = ""
        if self.dm_channels:
            from rich.markup import escape as _esc
            for ch in self.dm_channels[:8]:
                ch_id   = ch.get("id", "")
                pid, uname, dname = self._resolve_dm_participant(ch)
                name    = self._fmt_participant(dname, uname) if (uname or dname) else f"[dim]{(pid or '')[:8]}…[/]"
                active  = "▶ " if ch_id == self.current_ch else "  "
                unread  = f"[bold {GREEN}] ●[/]" if ch_id in self.unread else ""
                muted   = f" [dim {MUTED}]🔇[/]" if ch_id in self.muted else ""
                pstatus = self.presence_map.get(pid or "", "offline")
                pdot    = f"[bold {GREEN}]●[/] " if pstatus == "online" else "[dim]○[/] "
                dm_lines += f"[dim]{active}[/]{pdot}[dim]{_esc(name)}[/]{unread}{muted}\n"
        else:
            dm_lines = "[dim]  (none yet)[/]\n"

        guild_lines = ""
        if self.guilds:
            for g in self.guilds[:6]:
                gid    = g.get("id", "")
                gname  = g.get("name", "?")
                active = "▶ " if gid == self.current_guild_id else "  "
                guild_lines += f"[dim]{active}{gname}[/]\n"
        else:
            guild_lines = "[dim]  (none yet)[/]\n"

        sidebar = Panel(
            f"[bold {LIGHT_TEXT}]@{uname}[/]\n"
            f"[dim]{email}[/]\n\n"
            f"{status}\n\n"
            f"[dim {MUTED}]── Guilds ───[/]\n"
            f"{guild_lines}\n"
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
        # \x1b[3J clears scrollback so previous renders cannot be scrolled to
        sys.stdout.write("\x1b[3J")
        sys.stdout.flush()
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

    def _cmd_avatar(self, parts: list[str]):
        import os
        if len(parts) < 2:
            _error(self.console, "Usage: /avatar <path to image file>")
            self.console.input("  Press Enter…")
            return
        path = " ".join(parts[1:]).strip('"').strip("'")
        if not os.path.isfile(path):
            _error(self.console, f"File not found: {path}")
            self.console.input("  Press Enter…")
            return
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > 8:
            _error(self.console, f"File is {size_mb:.1f}MB — max allowed is 8MB.")
            self.console.input("  Press Enter…")
            return
        try:
            result = self.api.upload_avatar(path)
            avatar_url = result.get("avatar_url", "")
            self.user["avatar_url"] = avatar_url
            _success(self.console, f"Avatar updated!")
            if avatar_url:
                self.console.print(f"  [dim {MUTED}]URL: {self.api.base_url.rstrip('/api')}{avatar_url}[/]")
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
            pid, uname, dname = self._resolve_dm_participant(ch)
            name = self._fmt_participant(dname, uname) if (uname or dname) else (pid or "?")[:8] + "…"
            t.add_row(str(i), name, ch.get("id", ""))

        self.console.print(t)
        self.console.print(f"  [dim {MUTED}]Use /dm <username> to open a conversation.[/]")
        self.console.input("  Press Enter…")

    def _cmd_dm(self, parts: list[str]):
        if len(parts) < 2:
            _error(self.console, "Usage: /dm <username>")
            self.console.input("  Press Enter…")
            return

        target_username = parts[1]
        try:
            channel = self.api.open_dm(target_username)
        except Exception as e:
            _error(self.console, str(e))
            self.console.input("  Press Enter…")
            return

        ch_id     = channel.get("id")
        encrypted = channel.get("encrypted", 0)
        # Refresh DM list so sidebar has current participant info
        try:
            self.dm_channels = self.api.get_dm_channels()
        except Exception:
            pass
        ch_info = next((c for c in self.dm_channels if c.get("id") == ch_id), {})
        # Merge participants from open_dm response into ch_info if not already there
        # (the POST response has usernames; the GET list may lag until next refresh)
        if not ch_info.get("participants") and channel.get("participants"):
            ch_info = dict(ch_info)
            ch_info["participants"] = channel["participants"]
        pid, uname, dname = self._resolve_dm_participant(ch_info)
        name = self._fmt_participant(dname, uname or target_username)
        enc_tag = " [🔒]" if encrypted else ""

        self.current_ch       = ch_id
        self.current_ch_name  = f"DM:{name}{enc_tag}"
        self.current_guild_id = None
        self.messages         = []
        self.message_ids      = []
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

    def _cmd_guild(self, parts: list[str]):
        if len(parts) < 2:
            # No arg — list all guilds the user is in
            if not self.guilds:
                self.console.print(f"  [dim {MUTED}]You are not in any guilds yet. Use /guild create <name> to make one.[/]")
                self.console.input("  Press Enter…")
                return
            t = Table(title="Your Guilds", box=box.ROUNDED, border_style=BLURPLE)
            t.add_column("#",     style=f"dim {MUTED}", width=4)
            t.add_column("Name",  style=f"bold {LIGHT_TEXT}")
            t.add_column("Owner ID", style=f"dim {MUTED}")
            my_id = self.user.get("id", "")
            for i, g in enumerate(self.guilds, 1):
                oid = g.get("owner_id", "")
                owner_label = "you" if oid == my_id else oid[:8] + "…"
                t.add_row(str(i), g.get("name", "?"), owner_label)
            self.console.print(t)
            self.console.print(f"  [dim {MUTED}]Use /guild <name or #> to view a guild.[/]")
            self.console.input("  Press Enter…")
            return

        if parts[1].lower() == "create":
            if len(parts) < 3:
                _error(self.console, "Usage: /guild create <name>")
                self.console.input("  Press Enter…")
                return
            name = " ".join(parts[2:])
            try:
                guild = self.api.create_guild(name)
                gname = guild.get("name", name)
                gid   = guild.get("id", "")
                self.guilds.append({"id": gid, "name": gname, "owner_id": self.user.get("id", "")})
                _success(self.console, f"Created guild '{gname}'!")
                self._show_guild_detail(guild)
            except Exception as e:
                _error(self.console, str(e))
                self.console.input("  Press Enter…")
            return

        query = " ".join(parts[1:])

        # Allow picking by number from the guild list
        if query.lstrip("#").isdigit():
            idx = int(query.lstrip("#")) - 1
            if 0 <= idx < len(self.guilds):
                guild_id = self.guilds[idx].get("id")
            else:
                _error(self.console, f"No guild #{idx + 1}. You are in {len(self.guilds)} guild(s).")
                self.console.input("  Press Enter…")
                return
        else:
            matches = [g for g in self.guilds if query.lower() in g.get("name", "").lower()]
            if not matches:
                _error(self.console, f"No guild matching '{query}'. Use /guild to list your guilds.")
                self.console.input("  Press Enter…")
                return
            if len(matches) > 1:
                self.console.print(f"\n  [bold {YELLOW}]Multiple guilds match '{query}':[/]\n")
                t = Table(box=box.ROUNDED, border_style=YELLOW)
                t.add_column("#",        style=f"dim {MUTED}", width=4)
                t.add_column("Name",     style=f"bold {LIGHT_TEXT}")
                t.add_column("Owner ID", style=f"dim {MUTED}")
                my_id = self.user.get("id", "")
                for i, g in enumerate(matches, 1):
                    oid = g.get("owner_id", "")
                    owner_label = "you" if oid == my_id else oid[:8] + "…"
                    t.add_row(str(i), g.get("name", "?"), owner_label)
                self.console.print(t)
                choice = self.console.input(f"  [bold {BLURPLE}]Pick a number (or Enter to cancel):[/] ").strip()
                if not choice or not choice.isdigit():
                    self.console.input("  Cancelled. Press Enter…")
                    return
                pick = int(choice) - 1
                if not 0 <= pick < len(matches):
                    _error(self.console, "Invalid choice.")
                    self.console.input("  Press Enter…")
                    return
                guild_id = matches[pick].get("id")
            else:
                guild_id = matches[0].get("id")

        try:
            guild = self.api.get_guild(guild_id)
            self._show_guild_detail(guild)
        except Exception as e:
            _error(self.console, str(e))
            self.console.input("  Press Enter…")

    def _show_guild_detail(self, guild: dict):
        """Render guild channels and members, then prompt to join a channel by number."""
        guild_id = guild.get("id", "")
        gname    = guild.get("name", "?")
        channels = guild.get("channels", [])
        members  = guild.get("members", [])

        owner_id   = guild.get("owner_id", "")
        owner_info = next((m for m in members if m.get("user_id") == owner_id), None)
        owner_name = self._fmt_participant(
            owner_info.get("displayName") if owner_info else None,
            owner_info.get("username", owner_id[:8] + "…") if owner_info else owner_id[:8] + "…"
        )

        self.console.print(f"\n  [bold {BLURPLE}]{gname}[/]  [dim {MUTED}]owner: {owner_name}[/]\n")

        t = Table(title="Channels", box=box.ROUNDED, border_style=BLURPLE)
        t.add_column("#",       style=f"dim {MUTED}", width=4)
        t.add_column("Channel", style=f"bold {LIGHT_TEXT}")
        for i, ch in enumerate(channels, 1):
            active = " ◄" if ch.get("id") == self.current_ch else ""
            t.add_row(str(i), f"#{ch.get('name', '?')}{active}")
        self.console.print(t)

        t2 = Table(title="Members", box=box.ROUNDED, border_style=BLURPLE)
        t2.add_column("User",     style=f"bold {LIGHT_TEXT}")
        t2.add_column("Role",     style=f"dim {MUTED}")
        t2.add_column("Nickname", style=f"dim {MUTED}")
        for m in members:
            crown = " 👑" if m.get("user_id") == owner_id else ""
            name  = self._fmt_participant(m.get("displayName"), m.get("username", "?")) + crown
            t2.add_row(name, m.get("role", ""), m.get("nickname") or "")
        self.console.print(t2)

        for ch in channels:
            ch_id = ch.get("id")
            self.channel_guild_map[ch_id] = guild_id
            self.channel_name_map[ch_id]  = ch.get("name", ch_id)

        if channels:
            choice = self.console.input(f"\n  [bold {BLURPLE}]Join channel # (or Enter to cancel):[/] ").strip()
            if choice and choice.isdigit():
                pick = int(choice) - 1
                if 0 <= pick < len(channels):
                    ch_id   = channels[pick].get("id")
                    ch_name = channels[pick].get("name", ch_id)
                    if not self._open_channel(ch_id, f"#{ch_name}", guild_id):
                        pass  # error already shown, Press Enter consumed
                else:
                    _error(self.console, "Invalid channel number.")

    def _open_channel(self, channel_id: str, display_name: str, guild_id: str = None) -> bool:
        """Open a channel by ID, load history, and set as active. Returns True on success."""
        try:
            history = self.api.get_messages(channel_id, limit=50)
            self.current_ch       = channel_id
            self.current_ch_name  = display_name
            self.current_guild_id = guild_id
            self.messages         = []
            self.message_ids      = []
            self.unread.discard(channel_id)
            for msg in reversed(history):
                author  = msg.get("author_display_name") or msg.get("author_username", "?")
                content = msg.get("content", "")
                ts      = self._fmt_ts(msg.get("created_at"))
                edited  = bool(msg.get("edited_at"))
                self.messages.append((author, content, ts, edited))
                self.message_ids.append(msg.get("id"))
            return True
        except Exception as e:
            _error(self.console, str(e))
            self.console.input("  Press Enter…")
            return False

    def _cmd_join(self, parts: list[str]):
        """Join a channel by its ID. Use /guild <name> to browse channels and pick by number."""
        if len(parts) < 2:
            _error(self.console, "Usage: /join <channel_id>  — tip: use /guild <name> to browse and pick channels interactively")
            self.console.input("  Press Enter…")
            return
        channel_id = parts[1].lstrip("#")
        guild_id   = self.channel_guild_map.get(channel_id)
        ch_name    = self.channel_name_map.get(channel_id, channel_id[:8] + "…")
        self._open_channel(channel_id, f"#{ch_name}", guild_id)

    def _cmd_joinserver(self, parts: list[str]):
        """Join a guild by ID using POST /guilds/:id/members."""
        if len(parts) < 2:
            _error(self.console, "Usage: /joinserver <guild_id>")
            self.console.input("  Press Enter…")
            return
        guild_id = parts[1]
        try:
            self.api.join_guild(guild_id)
            # Refresh guild list
            self.guilds = self.api.get_guilds()
            _success(self.console, f"Joined guild! Use /guild to see your guilds.")
        except Exception as e:
            _error(self.console, str(e))
        self.console.input("  Press Enter…")

    def _resolve_dm_participant(self, ch: dict) -> tuple[str | None, str | None, str | None]:
        """Return (participant_id, username, display_name) for a DM channel dict.
        Reads username directly from participants array (now included by API).
        display_name is not in the DM channel list — returns None for it.
        """
        my_id = self.user.get("id")
        other = next(
            (p for p in ch.get("participants", []) if p.get("user_id") != my_id),
            None
        )
        if not other:
            return None, None, None
        return other.get("user_id"), other.get("username"), None

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

        # Send TYPING_START as soon as user is prompted (best-effort)
        if self.current_ch:
            try:
                import json as _json
                if hasattr(self, "_gateway") and self._gateway and self._gateway._ws:
                    self._gateway._ws.send(_json.dumps({
                        "op": "TYPING_START",
                        "data": {"channelId": self.current_ch}
                    }))
            except Exception:
                pass

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
            # Also re-render if a typing indicator is about to expire
            has_typing = any(
                any(exp <= now for exp in ch_typers.values())
                for ch_typers in self.typing_users.values()
            )
            if self._pending_render or has_expiring or has_typing:
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

                elif cmd == "/avatar":
                    self._cmd_avatar(parts)

                elif cmd == "/dms":
                    self._cmd_dms()

                elif cmd == "/dm":
                    self._cmd_dm(parts)

                elif cmd == "/guild":
                    self._cmd_guild(parts)

                elif cmd == "/join":
                    self._cmd_join(parts)

                elif cmd == "/joinserver":
                    self._cmd_joinserver(parts)

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