from sparks.router.resource.monitor import ResourceMonitor


def test_resource_monitor_returns_snapshot():
    monitor = ResourceMonitor()

    snapshot = monitor.snapshot()

    assert 0.0 <= snapshot.cpu_percent <= 100.0
    assert 0.0 <= snapshot.memory_percent <= 100.0
    assert snapshot.free_vram_mb >= 0
