# Skin Terminal Client

A Rich TUI terminal client for [Skeleton](https://github.com/Qazaroth/skeleton), the backend that powers it.

> **Note:** This project is developed in my spare time — progress may come and go depending on availability. Bear with me!

> **AI Disclosure:** This project is built with the assistance of [Claude](https://claude.ai) by Anthropic.

## Setup

Make sure [Python 3.10+](https://www.python.org/downloads/) is installed, then just run the appropriate script for your platform — it will handle installing dependencies automatically on first launch.

**Windows** — double-click `run.bat`

**Linux / Mac** — open a terminal in the project folder and run:
```bash
chmod +x run.sh
./run.sh
```

### Manual setup
If you'd prefer to run it yourself:
```bash
pip install -r requirements.txt
python main.py
```

## Features

- **Login / Register** — full auth flow with token storage & auto-refresh
- **Profile viewer** — `/me` shows your account details in a table
- **Profile editor** — `/edit <field> <value>` patches your profile via `PATCH /users/@me`
- **Message shell** — type freely; messages render in a scrollable history pane
- **Sidebar** — shows your username, status, and placeholders for servers/DMs

## Commands

| Command | Description |
|---|---|
| `/help` | Show all commands |
| `/me` | Fetch & display your profile |
| `/edit <field> <val>` | Update a profile field |
| `/logout` | Log out and return to welcome screen |
| `/quit` | Exit the client |

## Extending (when backend grows)

### Adding WebSocket support
1. `pip install websocket-client`
2. In `app.py`, create a `WSClient` thread after login that listens for events
3. In `ChatShell`, replace `_fake_send()` with a real WS send call
4. Push incoming messages into `self.messages` and call `_full_render()`

### Adding channels/servers
1. Add `GET /channels`, `GET /servers` calls to `api_client.py`
2. Populate the sidebar in `screens.py → ChatShell._render_sidebar_and_input()`
3. Add `/join <channel>` command to `ChatShell.run()`

### Adding Direct Messages
1. Add `GET /dm/:userId`, `POST /dm/:userId` to `api_client.py`
2. Add `/dm <username>` command that switches `self.current_ch` and loads history

## Project Structure

```
skin/
├── main.py          # Entry point
├── app.py           # App controller / screen orchestration
├── api_client.py    # REST API wrapper (auth, users, future endpoints)
├── screens.py       # All Rich TUI screens and the ChatShell
└── requirements.txt
```