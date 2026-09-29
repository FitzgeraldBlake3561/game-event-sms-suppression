from sms_gateway import LiveEvent, ModerationQueue, PlayerAsset, decide_send


def test_opt_out_wins_over_approved_live_event():
    player = PlayerAsset("p1", "+15555550123", sms_opted_out=True)
    event = LiveEvent("e1", "Raid", live=True)
    queue = ModerationQueue(frozenset({"e1"}))
    assert decide_send(player, event, queue) == type(decide_send(player, event, queue))(False, "player opted out")


def test_unmoderated_event_is_suppressed():
    player = PlayerAsset("p1", "+15555550123")
    event = LiveEvent("e1", "Raid")
    assert decide_send(player, event, ModerationQueue(frozenset())) .allowed is False

