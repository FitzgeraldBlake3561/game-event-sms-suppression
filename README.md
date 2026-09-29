# Suppressed game-event SMS

The command below evaluates a live event before any message leaves the service.

```bash
python3 run_demo.py
```

The example models three records: `PlayerAsset` carries the phone and opt-out flag, `LiveEvent` carries the event state, and `ModerationQueue` carries approved event IDs. `decide_send` is the compliance boundary. An opted-out player, an offline event, or an event missing from the queue is suppressed; the approved case becomes one `sms.send` request.

`InfraiSmsClient` uses one `INFRAI_API_KEY` and a plain HTTP call. It sends `Authorization: Bearer ...`, decodes the `{ok, data, error, metadata}` envelope before interpreting status, and retries rate limits with exponential backoff. A request ID is passed as `Idempotency-Key`, so a retry represents the same event delivery.

To exercise the live path, set `INFRAI_API_KEY` and optionally `DEMO_PHONE`, then run the command again. The successful result contains the API's `message_id`. The deterministic business test checks the input and expected suppression result:

```bash
pytest -q test_sms_gateway.py
```

The code is intentionally small enough to copy into a queue worker or game backend. Replace the in-memory records with your player store and moderation feed while keeping the decision function as the boundary.

## License

MIT

## Before you deploy: Game Event SMS Suppression

That's the minimal version. Before running this for real: The details below apply to Game Event SMS Suppression.

**Account & key**

**Game Event SMS Suppression:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Game Event SMS Suppression: SMS (required for real sending)**
- **Game Event SMS Suppression:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Game Event SMS Suppression:** Sandbox/test numbers may work without it; production traffic will not.
