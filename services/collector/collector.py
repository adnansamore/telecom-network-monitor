import os, time, yaml
from datetime import datetime
from sqlalchemy import create_engine, text
from utils import run_ping, run_iperf3_client
from alerts import send_alert


DB_PATH = os.getenv("DB_PATH", "/data/network.db")
CONFIG_PATH = os.getenv("CONFIG_PATH", "/app/config.yaml")
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pings (
id INTEGER PRIMARY KEY AUTOINCREMENT,
ts TEXT NOT NULL,
target TEXT NOT NULL,
latency_ms REAL,
success INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS bandwidth (
id INTEGER PRIMARY KEY AUTOINCREMENT,
ts TEXT NOT NULL,
target TEXT NOT NULL,
mbps REAL
);
"""

def init_db():
    with engine.begin() as conn:
        for stmt in SCHEMA_SQL.strip().split(";\n"):
            if stmt.strip():
                conn.execute(text(stmt))


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def record_ping(target, latency, success):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO pings(ts, target, latency_ms, success) VALUES(:ts,:t,:l,:s)"),
            {"ts": datetime.utcnow().isoformat(), "t": target, "l": latency, "s": int(success)}
        )


def record_bandwidth(target, mbps):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO bandwidth(ts, target, mbps) VALUES(:ts,:t,:m)"),
            {"ts": datetime.utcnow().isoformat(), "t": target, "m": mbps}
        )


def evaluate_alerts(cfg):
    with engine.begin() as conn:
        ping_row = conn.execute(
            text("SELECT target, latency_ms, success FROM pings ORDER BY id DESC LIMIT 1")
        ).fetchone()
        bw_row = conn.execute(
            text("SELECT target, mbps FROM bandwidth ORDER BY id DESC LIMIT 1")
        ).fetchone()
        if ping_row and (not ping_row.success or (ping_row.latency_ms and ping_row.latency_ms > cfg['thresholds']['max_latency_ms'])):
            send_alert(f"Ping alert {ping_row.target}: {ping_row.latency_ms} ms")
        if bw_row and (bw_row.mbps is None or bw_row.mbps < cfg['thresholds']['min_bandwidth_mbps']):
            send_alert(f"Bandwidth alert {bw_row.target}: {bw_row.mbps} Mbps")


def main():
    cfg = load_config()
    init_db()
    ping_interval = cfg['intervals']['ping_seconds']
    bw_interval = cfg['intervals']['bandwidth_seconds']
    last_bw = 0
    while True:
        for tgt in cfg['ping_targets']:
            latency, success = run_ping(tgt['host'])
            record_ping(tgt['name'], latency, success)
            print(f"Ping {tgt['name']} -> {latency} ms, success={success}")
        if time.time() - last_bw >= bw_interval:
            mbps = run_iperf3_client(
                cfg['bandwidth_target']['host'],
                cfg['bandwidth_target']['port'],
                cfg['bandwidth_target']['duration']
            )
            record_bandwidth(cfg['bandwidth_target']['host'], mbps)
            print(f"Bandwidth -> {mbps} Mbps")
            last_bw = time.time()
        evaluate_alerts(cfg)
        time.sleep(ping_interval)

if __name__ == "__main__":
    main()