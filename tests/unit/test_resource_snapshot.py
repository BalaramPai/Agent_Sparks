from sparks.router.resource.snapshot import ResourceSnapshot


def test_resource_snapshot_detects_available_memory():
    snapshot = ResourceSnapshot(
        cpu_percent=30.0,
        memory_percent=50.0,
        gpu_available=True,
        gpu_name="RTX 2050",
        total_vram_mb=4096,
        free_vram_mb=2048,
        used_vram_mb=2048,
    )

    assert snapshot.memory_available is True


def test_resource_snapshot_detects_memory_pressure():
    snapshot = ResourceSnapshot(
        cpu_percent=70.0,
        memory_percent=90.0,
        gpu_available=True,
        gpu_name="RTX 2050",
        total_vram_mb=4096,
        free_vram_mb=2048,
        used_vram_mb=2048,
    )

    assert snapshot.memory_available is False


def test_gpu_inference_availability():
    snapshot = ResourceSnapshot(
        cpu_percent=30.0,
        memory_percent=50.0,
        gpu_available=True,
        gpu_name="RTX 2050",
        total_vram_mb=4096,
        free_vram_mb=2048,
        used_vram_mb=2048,
    )

    assert snapshot.gpu_available_for_inference is True


def test_gpu_inference_unavailable_without_vram():
    snapshot = ResourceSnapshot(
        cpu_percent=30.0,
        memory_percent=50.0,
        gpu_available=True,
        gpu_name="RTX 2050",
        total_vram_mb=4096,
        free_vram_mb=0,
        used_vram_mb=4096,
    )

    assert snapshot.gpu_available_for_inference is False
