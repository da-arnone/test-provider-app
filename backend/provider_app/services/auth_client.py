import json
import os
from typing import Optional
from urllib import error, request as urlrequest


AUTH_APP_URL = os.getenv("AUTH_APP_URL", "http://localhost:8001").rstrip("/")
APP_SCOPE = "provider-app"
ALLOWED_PROVIDER_ROLES = {"provider-app", "provider-admin"}


def extract_bearer_token(request) -> Optional[str]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.replace("Bearer ", "", 1).strip() or None


def _post_json(path: str, payload: dict) -> Optional[dict]:
    url = f"{AUTH_APP_URL}{path}"
    body = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def issue_token(username: str, password: str) -> Optional[str]:
    payload = _post_json("/third/auth/token", {"username": username, "password": password})
    if not payload:
        return None
    return (payload.get("data") or {}).get("accessToken")


def whois(token: str) -> Optional[dict]:
    if not token:
        return None
    payload = _post_json("/third/auth/whois", {"token": token})
    if not payload:
        return None
    return payload.get("data") or None


def validate_token(token: str) -> Optional[dict]:
    if not token:
        return None
    payload = _post_json("/third/auth/validate", {"token": token})
    if not payload:
        return None
    data = payload.get("data") or {}
    if not data.get("valid"):
        return None
    return data.get("claims")


def authorize_request(token: str, required_role: str, context: Optional[str] = None) -> bool:
    if not token:
        return False
    payload = _post_json(
        "/third/auth/authorize",
        {
            "token": token,
            "appScope": APP_SCOPE,
            "requiredRole": required_role,
            "context": context,
        },
    )
    if not payload:
        return False
    return bool((payload.get("data") or {}).get("allowed"))


def _parse_provider_context(context) -> Optional[int]:
    if isinstance(context, int):
        return context
    if isinstance(context, str):
        digits = "".join(ch for ch in context if ch.isdigit())
        if digits:
            return int(digits)
    return None


def provider_ids_from_profiles(profiles: list[dict]) -> list[int]:
    provider_ids: list[int] = []
    for profile in profiles:
        if profile.get("appScope") != APP_SCOPE:
            continue
        if profile.get("role") not in ALLOWED_PROVIDER_ROLES:
            continue
        provider_id = _parse_provider_context(profile.get("context"))
        if provider_id is not None:
            provider_ids.append(provider_id)
    return sorted(set(provider_ids))


def has_provider_admin_profile(profiles: list[dict]) -> bool:
    for profile in profiles:
        if profile.get("appScope") != APP_SCOPE:
            continue
        if profile.get("role") == "provider-admin":
            return True
    return False
