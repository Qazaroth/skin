# Skin Terminal Client

A Rich TUI terminal client for [Skeleton](https://github.com/Qazaroth/skeleton), the backend that powers it.

> **Note:** This project is developed in my spare time — progress may come and go depending on availability. Bear with me!

> **AI Disclosure:** This project is built with the assistance of [Claude](https://claude.ai) by Anthropic.

---

## Setup

### Option 1 — Download the executable (recommended)

No Python required. Head to the [Releases](../../releases) page and download the file for your platform:

- **Windows** — download `skin.exe`, then double-click it
- **Linux** — download `skin`, then run:
  ```bash
  chmod +x skin
  ./skin
  ```

### Option 2 — Run from source

Make sure [Python 3.10+](https://www.python.org/downloads/) is installed, then run the appropriate script — it handles installing dependencies automatically on first launch.

**Windows** — double-click `scripts/run.bat`

**Linux / Mac** — open a terminal in the project folder and run:
```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

### Option 3 — Manual
```bash
pip install -r requirements.txt
python main.py
```

---

## Features

- **Auto login** — session is saved on exit and restored on next launch; only `/logout` clears it
- **Login / Register** — full auth flow with access token storage and silent auto-refresh
- **Real-time messaging** — WebSocket gateway connection with automatic reconnect and exponential backoff
- **Direct Messages** — open, list, and chat in DM channels; incoming messages appear instantly without pressing Enter
- **Unread indicators** — green dot on DM channels with unread messages when you are in a different conversation
- **Profile viewer** — `/me` shows your account details in a table
- **Profile editor** — `/edit <field> <value>` updates your profile (`username`, `displayName`, `avatar_url`)
- **Sidebar** — shows your username, gateway connection status, and DM channel list with display names and usernames
- **Server switcher** — `/config` lets you point the client at a different backend URL at runtime

---

## Commands

| Command | Description |
|---|---|
| `/help` | Show all commands |
| `/me` | Fetch and display your profile |
| `/edit <field> <val>` | Update a profile field (`username`, `displayName`, `avatar_url`) |
| `/dms` | List all your DM conversations |
| `/dm <username>` | Open a DM with a user and load message history |
| `/config` | Show or change the backend server URL |
| `/logout` | Log out, clear session, and return to the welcome screen |
| `/quit` | Exit the client (session is preserved for next launch) |

---

## Project Structure

```
skin/
├── src/
│   ├── app.py           # App controller and screen orchestration
│   ├── api_client.py    # REST API wrapper (auth, users, channels, messages)
│   ├── gateway.py       # WebSocket gateway client (IDENTIFY, READY, MESSAGE_CREATE)
│   ├── config.py        # Config loader / saver (base_url, session cookies)
│   └── screens.py       # All Rich TUI screens and the ChatShell
├── scripts/
│   ├── run.bat          # Windows launcher (auto-installs dependencies)
│   └── run.sh           # Linux / Mac launcher (auto-installs dependencies)
├── main.py              # Entry point
├── requirements.txt
└── README.md
```

---

## Notes

- `session.json` is created next to `main.py` after first login and used for auto-login on subsequent launches. It stores only the refresh token cookie — never the access token.
- The WebSocket gateway currently supports `IDENTIFY`, `READY`, and `MESSAGE_CREATE`. Further events (`MESSAGE_UPDATE`, `MESSAGE_DELETE`, `PRESENCE_UPDATE` etc.) will be added as the backend implements them.
- Real-time message display on Windows requires no extra setup — the client uses a background thread for input so the screen can update without waiting for Enter.