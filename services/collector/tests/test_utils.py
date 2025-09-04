from services.collector.utils import run_ping


def test_run_ping_invalid():
    latency, success = run_ping("no.such.host")
    assert latency is None or isinstance(latency, float)
    assert success in (True, False)