import os
import json
import time
import requests
from pathlib import Path
from cloaksmith.log import get_logger

log = get_logger()


class AuthSession:
    def __init__(self, base_url, realm, client_id, no_cache=False):
        self.base_url = base_url
        self.realm = realm
        self.client_id = client_id
        self.no_cache = no_cache
        if os.name == "nt":
            cache_dir = Path(os.getenv("LOCALAPPDATA")) / "cloaksmith"
        else:
            cache_dir = Path.home() / ".cache" / "cloaksmith"
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = cache_dir / "token.json"
        self.token_set = None
        if not self.no_cache:
            self._load_cached_token()

    def _cache_token(self):
        """
        Cache the token to a file.
        """
        if self.no_cache:
            return
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with self.cache_path.open("w") as f:
                json.dump({
                    "realm": self.realm,
                    "client_id": self.client_id,
                    "token": self.token_set
                }, f)
            log.info("Token cached successfully.")
        except Exception as e:
            log.error(f"Failed to cache token: {e}")

    def _load_cached_token(self):
        """
        Load the cached token from a file.
        """
        if not self.cache_path.exists():
            return
        try:
            with self.cache_path.open() as f:
                data = json.load(f)

            if data["realm"] != self.realm or data["client_id"] != self.client_id:
                return

            token = data["token"]
            issued_at = token.get("timestamp", 0)
            expires_in = token.get("expires_in", 0)

            if time.time() < issued_at + expires_in - 10:
                self.token_set = token
                log.info("Loaded cached access token.")
            else:
                self.token_set = token
                log.info(
                    "Cached token expired. Will attempt refresh on first request.")
        except Exception as e:
            log.warning(f"Failed to load cached token: {e}")

    def authenticate(self):
        """
        Authenticate the user by obtaining an access token.
        """
        try:
            if self.token_set:
                return

            device_url = f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/auth/device"
            token_url = f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/token"

            res = requests.post(device_url, data={"client_id": self.client_id})
            res.raise_for_status()
            device = res.json()

            direct_link = f"{device['verification_uri']}?user_code={device['user_code']}"
            log.info(f"Go to the following URL to authenticate: {direct_link}")

            while True:
                poll = requests.post(token_url, data={
                    "client_id": self.client_id,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device["device_code"]
                })
                if poll.status_code == 200:
                    self.token_set = poll.json()
                    self.token_set["timestamp"] = int(time.time())
                    self._cache_token()
                    log.info("Authentication successful.")
                    return
                elif poll.status_code in (400, 428):
                    continue
                else:
                    log.error(f"Authentication failed: {poll.text}")
                    raise Exception(f"Authentication failed: {poll.text}")
        except Exception as e:
            log.error(f"Error during authentication: {e}")
            raise

    def refresh_token(self):
        """
        Refresh the access token using the refresh token.
        """
        try:
            token_url = f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/token"
            res = requests.post(token_url, data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": self.token_set["refresh_token"],
            })
            res.raise_for_status()
            self.token_set = res.json()
            self.token_set["timestamp"] = int(time.time())
            self._cache_token()
            log.info("Token refreshed.")
        except Exception as e:
            log.error(f"Failed to refresh token: {e}")
            raise

    def request(self, method, url, **kwargs):
        """
        Make an authenticated request to the specified URL.
        """
        try:
            if not self.token_set:
                raise Exception("Authentication required.")

            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self.token_set['access_token']}"
            headers["Content-Type"] = "application/json"
            kwargs["headers"] = headers

            res = requests.request(method, url, **kwargs)

            if res.status_code == 401:
                log.warning("Access token expired. Refreshing.")
                self.refresh_token()
                headers["Authorization"] = f"Bearer {self.token_set['access_token']}"
                kwargs["headers"] = headers
                res = requests.request(method, url, **kwargs)

            return res

        except Exception as e:
            log.error(f"Request failed: {e}")
            raise
