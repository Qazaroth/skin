"""API Client - Handles all REST communication with the backend"""

import requests
from typing import Optional


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class APIClient:
    def __init__(self, base_url: str = "http://localhost:3000/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.request(
                method, url, headers=self._headers(), timeout=10, **kwargs
            )
        except requests.ConnectionError:
            raise APIError("Cannot connect to server. Is the backend running?")
        except requests.Timeout:
            raise APIError("Request timed out.")

        try:
            data = resp.json()
        except Exception:
            data = {}

        if resp.status_code == 401:
            # On auth endpoints, surface the real backend error rather than intercepting
            if path.startswith("/auth/"):
                message = data.get("message") or data.get("error") or "Invalid credentials."
                raise APIError(message, 401)
            # On protected endpoints, attempt a token refresh
            if self.refresh_token:
                try:
                    self._refresh_access_token()
                    resp = self.session.request(
                        method, url, headers=self._headers(), timeout=10, **kwargs
                    )
                    try:
                        data = resp.json()
                    except Exception:
                        data = {}
                except APIError:
                    self.access_token = None
                    self.refresh_token = None
                    raise APIError("Session expired. Please log in again.", 401)
            else:
                raise APIError("Unauthorized. Please log in.", 401)

        if not resp.ok:
            message = data.get("message") or data.get("error") or f"HTTP {resp.status_code}"
            raise APIError(message, resp.status_code)

        return data

    def _refresh_access_token(self):
        resp = self.session.post(
            f"{self.base_url}/auth/refresh",
            json={"refreshToken": self.refresh_token},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if not resp.ok:
            raise APIError("Token refresh failed.", resp.status_code)
        data = resp.json()
        self.access_token = data.get("accessToken") or data.get("token")

    # ── Auth ──────────────────────────────────────────────────────────────────

    def register(self, username: str, email: str, password: str) -> dict:
        data = self._request(
            "POST", "/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        self._store_tokens(data)
        return data

    def login(self, login: str, password: str) -> dict:
        data = self._request(
            "POST", "/auth/login",
            json={"login": login, "password": password}
        )
        self._store_tokens(data)
        return data

    def logout(self) -> dict:
        try:
            data = self._request("POST", "/auth/logout", json={})
        except APIError:
            data = {}
        self.access_token = None
        self.refresh_token = None
        return data

    def _store_tokens(self, data: dict):
        self.access_token = (
            data.get("accessToken")
            or data.get("access_token")
            or data.get("token")
        )
        self.refresh_token = (
            data.get("refreshToken")
            or data.get("refresh_token")
        )

    # ── Users ─────────────────────────────────────────────────────────────────

    def get_me(self) -> dict:
        return self._request("GET", "/users/@me")

    def update_me(self, **fields) -> dict:
        return self._request("PATCH", "/users/@me", json=fields)

    @property
    def is_authenticated(self) -> bool:
        return self.access_token is not None