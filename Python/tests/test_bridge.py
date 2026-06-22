from app.bridge import smooth_cc, MidiBridge


def test_smooth_cc_blends_toward_new_value():
    assert smooth_cc(prev=0, val=100) == int(0 * 0.6 + 100 * 0.4)


def test_smooth_cc_snaps_to_127_near_max():
    assert smooth_cc(prev=50, val=124) == 127
    assert smooth_cc(prev=50, val=127) == 127


def test_smooth_cc_snaps_to_0_near_min():
    assert smooth_cc(prev=80, val=3) == 0
    assert smooth_cc(prev=80, val=0) == 0


def test_bridge_emit_cc_emits_smoothed_value(qtbot):
    bridge = MidiBridge()
    received = []
    bridge.cc.connect(lambda num, val: received.append((num, val)))

    with qtbot.waitSignal(bridge.cc, timeout=1000):
        bridge.emit_cc(1, 127)

    assert received == [(1, 127)]


def test_bridge_emit_note_on_off(qtbot):
    bridge = MidiBridge()
    with qtbot.waitSignal(bridge.note_on, timeout=1000) as blocker:
        bridge.emit_note_on(60, 100)
    assert blocker.args == [60, 100]

    with qtbot.waitSignal(bridge.note_off, timeout=1000) as blocker:
        bridge.emit_note_off(60, 0)
    assert blocker.args == [60, 0]
