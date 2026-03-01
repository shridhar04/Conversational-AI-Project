import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from conversational_agent.core.config import Settings


@dataclass(frozen=True)
class CurrentUser:
    username: str
    roles: list[str]


@dataclass(frozen=True)
class _StoredUser:
    username: str
    hashed_password: str
    roles: list[str]


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._users = self._load_users(settings.auth_users_json)

    def authenticate(self, username: str, password: str) -> CurrentUser | None:
        stored = self._users.get(username)
        if stored is None:
            return None
        if not self._pwd_context.verify(password, stored.hashed_password):
            return None
        return CurrentUser(username=stored.username, roles=stored.roles)

    def create_access_token(self, user: CurrentUser) -> str:
        expires = datetime.now(UTC) + timedelta(minutes=self._settings.access_token_expire_minutes)
        payload = {"sub": user.username, "roles": user.roles, "exp": expires}
        return jwt.encode(payload, self._settings.auth_secret_key, algorithm=self._settings.auth_algorithm)

    def decode_access_token(self, token: str) -> CurrentUser | None:
        try:
            payload = jwt.decode(
                token,
                self._settings.auth_secret_key,
                algorithms=[self._settings.auth_algorithm],
            )
        except JWTError:
            return None
        sub = payload.get("sub")
        roles = payload.get("roles")
        if not isinstance(sub, str) or not isinstance(roles, list):
            return None
        parsed_roles = [str(role) for role in roles]
        return CurrentUser(username=sub, roles=parsed_roles)

    def _load_users(self, raw: str) -> dict[str, _StoredUser]:
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError("AUTH_USERS_JSON must be a JSON array")
        users: dict[str, _StoredUser] = {}
        for item in payload:
            if not isinstance(item, dict):
                continue
            username = str(item.get("username", "")).strip()
            password = str(item.get("password", ""))
            roles = item.get("roles", [])
            if not username or not password or not isinstance(roles, list):
                continue
            parsed_roles = [str(role).strip() for role in roles if str(role).strip()]
            if not parsed_roles:
                continue
            hashed_password = (
                password if password.startswith("$2") else self._pwd_context.hash(password)
            )
            users[username] = _StoredUser(
                username=username, hashed_password=hashed_password, roles=parsed_roles
            )
        if not users:
            raise ValueError("No valid users configured in AUTH_USERS_JSON")
        return users
