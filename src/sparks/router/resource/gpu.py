from dataclasses import dataclass

import pynvml


@dataclass(frozen=True)
class GPUInfo:
    available: bool
    name: str | None
    total_vram_mb: int
    free_vram_mb: int
    used_vram_mb: int


class GPUMonitor:
    """
    Reads NVIDIA GPU and VRAM information.

    Failure to access an NVIDIA GPU is treated as a normal
    capability state rather than a fatal runtime error.
    """

    def snapshot(self) -> GPUInfo:
        try:
            pynvml.nvmlInit()

            device_count = pynvml.nvmlDeviceGetCount()

            if device_count == 0:
                return GPUInfo(
                    available=False,
                    name=None,
                    total_vram_mb=0,
                    free_vram_mb=0,
                    used_vram_mb=0,
                )

            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)

            name = pynvml.nvmlDeviceGetName(handle)

            if isinstance(name, bytes):
                name = name.decode("utf-8")

            return GPUInfo(
                available=True,
                name=name,
                total_vram_mb=memory.total // (1024 * 1024),
                free_vram_mb=memory.free // (1024 * 1024),
                used_vram_mb=memory.used // (1024 * 1024),
            )

        except Exception:
            return GPUInfo(
                available=False,
                name=None,
                total_vram_mb=0,
                free_vram_mb=0,
                used_vram_mb=0,
            )

        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass