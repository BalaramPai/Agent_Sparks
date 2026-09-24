from sparks.router.resource.governor import ResourceGovernor, ResourceLevel
from sparks.router.resource.snapshot import ResourceSnapshot


def make_snapshot(
    cpu: float = 30.0,
    memory: float = 50.0,
    free_vram: int = 2048,
) -> ResourceSnapshot:
    return ResourceSnapshot(
        cpu_percent=cpu,
        memory_percent=memory,
        gpu_available=True,
        gpu_name="RTX 2050",
        total_vram_mb=4096,
        free_vram_mb=free_vram,
        used_vram_mb=4096 - free_vram,
    )


def test_normal_resources():
    governor = ResourceGovernor()

    result = governor.evaluate(make_snapshot())

    assert result == ResourceLevel.NORMAL


def test_high_memory_creates_constrained_state():
    governor = ResourceGovernor()

    result = governor.evaluate(
        make_snapshot(memory=85.0)
    )

    assert result == ResourceLevel.CONSTRAINED


def test_high_cpu_creates_critical_state():
    governor = ResourceGovernor()

    result = governor.evaluate(
        make_snapshot(cpu=95.0)
    )

    assert result == ResourceLevel.CRITICAL


def test_low_vram_creates_constrained_state():
    governor = ResourceGovernor()

    result = governor.evaluate(
        make_snapshot(free_vram=800)
    )

    assert result == ResourceLevel.CONSTRAINED


def test_very_low_vram_creates_critical_state():
    governor = ResourceGovernor()

    result = governor.evaluate(
        make_snapshot(free_vram=400)
    )

    assert result == ResourceLevel.CRITICAL