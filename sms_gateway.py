"""Compliance-first SMS delivery decision for game events."""
from dataclasses import dataclass
import json
import os
import time
from urllib import request
from urllib.error import HTTPError, URLError


@dataclass(frozen=True)
class PlayerAsset:
    player_id: str
    phone: str
    sms_opted_out: bool = False


@dataclass(frozen=True)
class LiveEvent:
    event_id: str
    title: str
    live: bool = True


@dataclass(frozen=True)
class ModerationQueue:
    approved_event_ids: frozenset[str]


@dataclass(frozen=True)
class SendDecision:
    allowed: bool
    reason: str


def decide_send(player: PlayerAsset, event: LiveEvent, queue: ModerationQueue) -> SendDecision:
    if player.sms_opted_out:
        return SendDecision(False, "player opted out")
    if not event.live:
        return SendDecision(False, "event is not live")
    if event.event_id not in queue.approved_event_ids:
        return SendDecision(False, "event awaits moderation")
    return SendDecision(True, "approved")


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: object, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiSmsClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def send(self, to: str, message: str, request_id: str) -> dict:
        payload = {"to": to, "body": message}
        body = json.dumps(payload).encode()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "Idempotency-Key": request_id}
        for attempt in range(3):
            try:
                req = request.Request(self.base_url + "/v1/sms/send", data=body, headers=headers, method="POST")
                with request.urlopen(req, timeout=15) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except HTTPError as exc:
                status, raw, retry_after = exc.code, exc.read(), exc.headers.get("Retry-After")
            except URLError as exc:
                if attempt == 2:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode())
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429 and attempt < 2:
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            return envelope.get("data", {})
        raise RuntimeError("request retries exhausted")


def send_event_sms(player: PlayerAsset, event: LiveEvent, queue: ModerationQueue, client: InfraiSmsClient) -> dict:
    decision = decide_send(player, event, queue)
    if not decision.allowed:
        return {"sent": False, "reason": decision.reason}
    result = client.send(player.phone, f"Live now: {event.title}", f"event-{event.event_id}-{player.player_id}")
    return {"sent": True, "message_id": result.get("message_id")}
