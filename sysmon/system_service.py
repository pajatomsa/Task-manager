from dataclasses import dataclass
import psutil


@dataclass
class ProcessInfo:
    pid: int
    name: str
    username: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str


@dataclass
class HardwareMetrics:
    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    total_processes: int
    cpu_count_logical: int = 1


class SystemService:
    def __init__(self) -> None:
        try:
            psutil.cpu_percent(interval=None)
        except Exception:
            pass

    def get_hardware_metrics(self) -> HardwareMetrics:
        try:
            mem = psutil.virtual_memory()
            return HardwareMetrics(
                cpu_percent=psutil.cpu_percent(interval=None) or 0.0,
                ram_percent=mem.percent,
                ram_used_gb=round(mem.used / (1024**3), 1),
                ram_total_gb=round(mem.total / (1024**3), 1),
                total_processes=len(psutil.pids()),
                cpu_count_logical=psutil.cpu_count() or 1,
            )
        except Exception:
            return HardwareMetrics(0.0, 0.0, 0.0, 0.0, 0, 1)

    def get_processes(
        self,
        sort_by: str = "cpu_percent",
        reverse: bool = True,
        filter_text: str = "",
    ) -> list[ProcessInfo]:
        procs = []
        attrs = [
            "pid",
            "name",
            "username",
            "cpu_percent",
            "memory_percent",
            "memory_info",
            "status",
        ]
        for p in psutil.process_iter(attrs=attrs, ad_value=None):
            try:
                info = p.info
                name = info.get("name") or "neznámý"
                pid = info.get("pid") or 0
                if filter_text and filter_text.lower() not in f"{name} {pid}".lower():
                    continue

                mem = info.get("memory_info")
                procs.append(
                    ProcessInfo(
                        pid=pid,
                        name=name,
                        username=info.get("username") or "-",
                        cpu_percent=round(info.get("cpu_percent") or 0.0, 1),
                        memory_percent=round(info.get("memory_percent") or 0.0, 1),
                        memory_mb=round(mem.rss / (1024**2), 1) if mem else 0.0,
                        status=str(info.get("status") or "running"),
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        procs.sort(key=lambda x: getattr(x, sort_by, 0), reverse=reverse)
        return procs

    def terminate_process(self, pid: int) -> tuple[bool, str]:
        try:
            psutil.Process(pid).terminate()
            return True, f"Proces {pid} byl ukončen."
        except psutil.NoSuchProcess:
            return False, f"Proces {pid} již neexistuje."
        except psutil.AccessDenied:
            return False, f"Přístup odepřen pro PID {pid}."
        except Exception as e:
            return False, str(e)
