import json
import os

from sms_gateway import InfraiSmsClient, LiveEvent, ModerationQueue, PlayerAsset, send_event_sms


player = PlayerAsset("player-42", os.environ.get("DEMO_PHONE", "+15555550123"), sms_opted_out=False)
event = LiveEvent("final-2026", "Championship final")
queue = ModerationQueue(frozenset({"final-2026"}))

if os.environ.get("INFRAI_API_KEY"):
    result = send_event_sms(player, event, queue, InfraiSmsClient())
else:
    result = {"sent": False, "reason": "set INFRAI_API_KEY to send; decision approved"}
print(json.dumps(result))

