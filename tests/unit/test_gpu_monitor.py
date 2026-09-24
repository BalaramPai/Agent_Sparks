from sparks.router.resource.gpu import GPUMonitor


def test_gpu_monitor_returns_valid_snapshot():
    monitor = GPUMonitor()

    gpu = monitor.snapshot()

    assert gpu.total_vram_mb >= 0
    assert gpu.free_vram_mb >= 0
    assert gpu.used_vram_mb >= 0

    if gpu.available:
        assert gpu.name is not None
        assert gpu.total_vram_mb > 0