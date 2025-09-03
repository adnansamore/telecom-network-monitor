import os
from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine, text


DB_PATH = os.getenv("DB_PATH", "/data/network.db")
PORT = int(os.getenv("FLASK_RUN_PORT", 8000))
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
app = Flask(__name__)


@app.route("/api/pings")
def pings():
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                "SELECT ts, target, latency_ms, success FROM pings ORDER BY id DESC LIMIT 200"
            )
        ).mappings().all()
        # Convert each RowMapping to dict
        result = [dict(row) for row in rows]
        return jsonify(result)


@app.route("/api/bandwidth")
def bandwidth():
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT ts, target, mbps FROM bandwidth ORDER BY id DESC LIMIT 200")
        ).mappings().all()
        # Convert each RowMapping to dict
        result = [dict(row) for row in rows]
        return jsonify(result)



@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)