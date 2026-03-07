# Skin — Roadmap

This roadmap tracks planned, in-progress, and completed features for the Skin terminal client. It mirrors the Bodcord backend's development phases where relevant.

> Features are tied to what the backend exposes. Items marked as waiting on backend cannot be built until the server implements the relevant API or gateway events.

---

## Phase 1 — Core Client ✅

The essentials needed for a functional messaging client.

- [x] Project structure (`src/`, `scripts/`, `main.py`)
- [x] Config system (`config.json`, runtime `/config` command)
- [x] Rich TUI shell with sidebar and message pane
- [x] User registration with validation error display
- [x] User login (email or username)
- [x] Auto login via persisted refresh token cookie (`session.json`)
- [x] Silent token refresh on startup and mid-session 401s
- [x] Logout (clears session, returns to welcome screen)
- [x] `/quit` preserves session for next launch
- [x] Profile viewer (`/me`)
- [x] Profile editor (`/edit username | displayName | avatar_url`)
- [x] Avatar upload (`/avatar <path>`) — JPEG, PNG, GIF, WebP up to 8MB
- [x] Version display in header

---

## Phase 2 — Direct Messages ✅

- [x] Open a DM channel with a user by username (`/dm <username>`)
- [x] List all DM conversations (`/dms`)
- [x] Load message history on channel open (last 50 messages)
- [x] Display names shown as `Display Name (username)` throughout
- [x] Send messages to a DM channel
- [x] Edit your own messages by index (`/editmsg <#> <new content>`)
- [x] Delete your own messages by index (`/delmsg <#>`)
- [x] Message index numbers shown in chat (`#1`, `#2`…)

---

## Phase 3 — Real-time Gateway ✅

- [x] WebSocket gateway connection with IDENTIFY / READY flow
- [x] Heartbeat handling (`HEARTBEAT` → `HEARTBEAT_ACK`)
- [x] `heartbeatInterval` read from `READY` payload
- [x] `MESSAGE_CREATE` — incoming messages appear instantly
- [x] `MESSAGE_UPDATE` — edited messages update in place
- [x] `MESSAGE_DELETE` — deleted messages removed from view
- [x] Unread dot indicators in sidebar for background channels
- [x] Toast notifications for incoming DMs from other channels
- [x] Per-channel mute (`/mute [username]`) — suppresses toasts, keeps unread dot
- [x] Auto-reconnect with exponential backoff (2s → 4s → 8s → 60s cap)
- [x] Token refresh before reconnect after ungraceful disconnect
- [x] Close code handling (4001–4006) with appropriate actions
- [x] Non-blocking input on Windows via background stdin thread
- [x] Gateway status shown in sidebar (connecting / identifying / online)

---

## Phase 4 — Guild Channels 🔧

*Basic guild support is now available. Further guild features depend on backend progress.*

- [x] Create a guild (`/guild create <name>`)
- [x] View a guild's channels and members (`/guild <id>`)
- [x] Join and read a guild channel (`/join <channel_id>`)
- [x] Send messages to guild channels
- [x] Guild list — shown in sidebar, pre-loaded on login (`GET /users/@me/guilds`)
- [ ] Guild channels shown in sidebar
- [ ] Unread indicators for guild channels
- [ ] `/leave` — leave current guild channel

---

## Phase 5 — Presence & Typing ⏳

*Waiting on backend (`PRESENCE_UPDATE`, `TYPING_START` gateway events).*

- [ ] Show online/offline status for DM participants in sidebar
- [ ] Typing indicator — show `[user] is typing…` in chat
- [ ] Send typing events when user starts composing a message

---

## Phase 6 — Polish & UX 🔧

Improvements that can be worked on independently of backend progress.

- [ ] Scroll through message history (currently capped at last 20 shown)
- [ ] Pagination — load older messages with cursor (`before` param)
- [ ] `/search <query>` — filter messages in current channel
- [ ] Configurable message history limit
- [ ] Timestamps shown as relative time (`2 minutes ago`) with toggle
- [ ] Highlight messages that mention your username
- [ ] `/clear` — clear the current message view locally
- [ ] Persist muted channels across sessions
- [ ] Screenshots / assets in `assets/` folder for README

---

## Phase 7 — Release & Distribution 🔧

- [x] GitHub Actions CI — builds `skin.exe` (Windows) and `skin` (Linux) on version tags
- [x] PyInstaller `--paths src` fix for bundled executables
- [ ] macOS build added to release workflow
- [ ] Auto-update check on launch (`GET /health` version header, if added to backend)
- [ ] Versioned releases with changelogs on GitHub

---

## Out of Scope

These are intentionally not planned for Skin:

- **Voice / video** — Phase 4 backend feature requiring WebRTC; not suitable for a TUI
- **Image rendering** — terminal image rendering is fragile and platform-specific
- **Mobile** — a separate project would be more appropriate (e.g. Flutter)