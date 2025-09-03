import json
import subprocess
from typing import Optional, Tuple


def run_ping(host: str, count: int = 1, timeout: int = 2) -> Tuple[Optional[float], bool]:
    try:
        proc = subprocess.run(
            ["ping", "-c", str(count), "-W", str(timeout), host],
            capture_output=True, text=True, check=False
        )
        out = proc.stdout
        success = proc.returncode == 0
        latency = None
        for line in out.splitlines():
            if "min/avg/max" in line:
                stats = line.split("=")[-1].strip().split("/")
                latency = float(stats[1])
        return latency, success
    except Exception:
        return None, False


def run_iperf3_client(host: str, port: int = 5201, duration: int = 5) -> Optional[float]:
    try:
        cmd = ["iperf3", "-c", host, "-p", str(port), "-J", "-t", str(duration), "--logfile", "/dev/stdout"]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            return None
        data = json.loads(proc.stdout)
        return float(data["end"]["sum_received"]["bits_per_second"]) / 1e6
    except Exception:
        return None