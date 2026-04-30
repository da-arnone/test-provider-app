import json
import os
from typing import Any, Optional
from urllib import error, parse, request as urlrequest


SUBSCRIPTION_APP_URL = os.getenv(
    "SUBSCRIPTION_APP_URL",
    os.getenv("SUSCRIPTION_APP_URL", "http://localhost:8003"),
).rstrip("/")


def _request_json(
    path: str,
    token: Optional[str],
    method: str = "GET",
    body: Optional[dict[str, Any]] = None,
):
    data = None
    headers = {
        "Accept": "application/json",
        **({"Authorization": f"Bearer {token}"} if token else {}),
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urlrequest.Request(
        f"{SUBSCRIPTION_APP_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urlrequest.urlopen(req, timeout=8) as response:
            return json.loads(response.read().decode("utf-8")), None, None
    except error.HTTPError as exc:
        detail = None
        try:
            payload = json.loads(exc.read().decode("utf-8"))
            if isinstance(payload, dict):
                detail = payload.get("detail") or payload.get("message")
        except (UnicodeDecodeError, json.JSONDecodeError):
            detail = None
        return None, exc.code, detail
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        return None, 502, "subscription-app unavailable"


def list_incoming_submissions(token: str, provider_id: int):
    query = parse.urlencode(
        {
            "submitee_entity_type": "provider",
            "submitee_entity_id": provider_id,
        }
    )
    payload, status_code, detail = _request_json(f"/third/subscription/requests/?{query}", token)
    if status_code == 404:
        # Backward compatibility with older third API path spelling.
        return _request_json(f"/third/suscription/requests/?{query}", token)
    return payload, status_code, detail


def decide_incoming_submission(
    token: str,
    submission_id: int,
    *,
    status: str,
    decision_note: str = "",
    decision_metadata: Optional[dict[str, Any]] = None,
):
    payload: dict[str, Any] = {"status": status, "decision_note": decision_note}
    if decision_metadata is not None:
        payload["decision_metadata"] = decision_metadata
    path = f"/third/subscription/requests/{submission_id}/decision/"
    response_payload, status_code, detail = _request_json(
        path,
        token,
        method="PATCH",
        body=payload,
    )
    if status_code == 404:
        # Backward compatibility with older third API path spelling.
        return _request_json(
            f"/third/suscription/requests/{submission_id}/decision/",
            token,
            method="PATCH",
            body=payload,
        )
    return response_payload, status_code, detail


def has_handled_org_subscription(
    token: str,
    *,
    provider_id: int,
    organization_ids: list[int],
) -> bool:
    """
    Return True when at least one organization has a handled subscription
    to the given provider.
    """
    if not organization_ids:
        return False

    payload, status_code, _detail = list_incoming_submissions(token, provider_id=provider_id)
    if status_code or not isinstance(payload, list):
        return False

    org_id_set = set(organization_ids)
    for row in payload:
        if not isinstance(row, dict):
            continue
        status = (row.get("status") or "").lower()
        if status != "handled":
            continue

        submitting_type = (row.get("submitting_entity_type") or "").lower()
        if submitting_type not in {"organization", "org"}:
            continue

        try:
            submitting_id = int(row.get("submitting_entity_id"))
        except (TypeError, ValueError):
            continue
        if submitting_id in org_id_set:
            return True

    return False
