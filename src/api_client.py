"""API Client - Handles all REST communication with the Skeleton backend"""

import requests
from typing import Optional


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class APIClient:
    def __init__(self, base_url: str = "http://localhost:3000/api"):
        self.base_url    = base_url
        self.session     = requests.Session()  # session handles httpOnly cookie automatically
        self.access_token: Optional[str] = None

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.request(
                method, url, headers=self._headers(), timeout=10, **kwargs
            )
        except requests.ConnectionError:
            raise APIError("Cannot connect to server. Is the backend running?")
        except requests.Timeout:
            raise APIError("Request timed out.")

        # 204 No Content (e.g. DELETE)
        if resp.status_code == 204:
            return None

        try:
            data = resp.json()
        except Exception:
            data = {}

        if resp.status_code == 401:
            # On auth endpoints, surface the real backend error
            if path.startswith("/auth/"):
                message = data.get("error") or "Invalid credentials."
                raise APIError(message, 401)
            # On protected endpoints, attempt a token refresh via cookie
            try:
                self._refresh_access_token()
                resp = self.session.request(
                    method, url, headers=self._headers(), timeout=10, **kwargs
                )
                if resp.status_code == 204:
                    return None
                try:
                    data = resp.json()
                except Exception:
                    data = {}
            except APIError:
                self.access_token = None
                raise APIError("Session expired. Please log in again.", 401)

        if not resp.ok:
            message = data.get("error") or f"HTTP {resp.status_code}"
            raise APIError(message, resp.status_code)

        return data

    def _refresh_access_token(self):
        """Refresh using the httpOnly cookie — no body needed."""
        resp = self.session.post(
            f"{self.base_url}/auth/refresh",
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if not resp.ok:
            raise APIError("Token refresh failed.", resp.status_code)
        data = resp.json()
        self.access_token = data.get("token")

    # ── Auth ──────────────────────────────────────────────────────────────────

    def register(self, username: str, email: str, password: str) -> dict:
        """Returns the new user object. No token issued on register — login after."""
        return self._request(
            "POST", "/auth/register",
            json={"username": username, "email": email, "password": password}
        )

    def login(self, login: str, password: str) -> dict:
        """Returns the user dict and stores the access token."""
        data = self._request(
            "POST", "/auth/login",
            json={"login": login, "password": password}
        )
        # Response shape: { token: "...", user: { ... } }
        self.access_token = data.get("token")
        return data.get("user", data)

    def logout(self) -> None:
        try:
            self._request("POST", "/auth/logout")
        except APIError:
            pass
        self.access_token = None

    # ── Users ─────────────────────────────────────────────────────────────────

    def get_me(self) -> dict:
        return self._request("GET", "/users/@me")

    def update_me(self, **fields) -> dict:
        allowed = {k: v for k, v in fields.items() if k in ("username", "displayName", "avatar_url")}
        return self._request("PATCH", "/users/@me", json=allowed)

    # ── DM Channels ───────────────────────────────────────────────────────────

    def open_dm(self, username: str) -> dict:
        """Open or retrieve an existing DM channel with another user."""
        return self._request(
            "POST", "/users/@me/channels",
            json={"username": username}
        )

    def get_dm_channels(self) -> list:
        """Get all DM channels for the current user."""
        return self._request("GET", "/users/@me/channels") or []

    # ── Messages ──────────────────────────────────────────────────────────────

    def send_message(self, channel_id: str, content: str) -> dict:
        return self._request(
            "POST", f"/channels/{channel_id}/messages",
            json={"content": content}
        )

    def get_messages(self, channel_id: str, limit: int = 50, before: Optional[str] = None) -> list:
        params = {"limit": limit}
        if before:
            params["before"] = before
        return self._request("GET", f"/channels/{channel_id}/messages", params=params) or []

    def edit_message(self, channel_id: str, message_id: str, content: str) -> dict:
        return self._request(
            "PATCH", f"/channels/{channel_id}/messages/{message_id}",
            json={"content": content}
        )

    def delete_message(self, channel_id: str, message_id: str) -> None:
        self._request("DELETE", f"/channels/{channel_id}/messages/{message_id}")

    # ── System ────────────────────────────────────────────────────────────────

    def health(self) -> dict:
        return self._request("GET", "/health")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def is_authenticated(self) -> bool:
        return self.access_token is not None