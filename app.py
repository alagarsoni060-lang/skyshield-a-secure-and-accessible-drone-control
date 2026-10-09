import os
import hmac
import sqlite3
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

API_KEY = os.environ.get("SKYSHIELD_API_KEY", "")
DB_PATH = os.environ.get("SKYSHIELD_DB", "skyshield.db")

# Local demo origins. Configure your actual frontend origin for deployment.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "SKYSHIELD_ALLOWED_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500"
    ).split(",")
    if origin.strip()
]

CORS(app, resources={
    r"/api/*": {"origins": ALLOWED_ORIGINS}
})

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["120 per minute"],
    storage_uri="memory://"
)

# Demo flight boundaries. Adjust for your simulator test area.
GEOFENCE = {
    "min_lat": 10.80,
    "max_lat": 10.90,
    "min_lon": 76.20,
    "max_lon": 76.32
}

MAX_GPS_JUMP = 0.01
MIN_SIGNAL = 25
ALLOWED_COMMANDS = {"UP", "DOWN", "LEFT", "RIGHT", "LAND"}

drone = {
    "id": "DRONE-01",
    "connection": "OFFLINE",
    "authenticated": False,
    "threat_status": "PROTECTED",
    "spoof_detected": False,
    "battery": 94,
    "latitude": 10.8506,
    "longitude": 76.2711,
    "altitude": 120,
    "signal_strength": 95,
    "signal_integrity": "SECURE",
    "command_verification": "ACTIVE",
    "emergency_stop": False,
    "mode": "SIMULATION"
}

last_sequence = -1
previous_position = (
    drone["latitude"],
    drone["longitude"]
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                event TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                command TEXT NOT NULL,
                result TEXT NOT NULL
            )
        """)


def log_event(message, level="INFO"):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO events(timestamp, level, event)
               VALUES (?, ?, ?)""",
            (utc_now(), level, message)
        )


def require_api_key(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not API_KEY:
            return jsonify({
                "error": "Server API key is not configured."
            }), 503

        supplied_key = request.headers.get("X-API-Key", "")

        if not hmac.compare_digest(supplied_key, API_KEY):
            log_event("Rejected request: invalid API key", "WARNING")
            return jsonify({"error": "Unauthorized"}), 401

        return function(*args, **kwargs)

    return wrapper


def inside_geofence(latitude, longitude):
    return (
        GEOFENCE["min_lat"] <= latitude <= GEOFENCE["max_lat"]
        and GEOFENCE["min_lon"] <= longitude <= GEOFENCE["max_lon"]
    )


def security_summary():
    return {
        "score": 0 if drone["spoof_detected"] else 100,
        "authentication": (
            "VERIFIED" if drone["authenticated"] else "UNVERIFIED"
        ),
        "signal_integrity": drone["signal_integrity"],
        "spoof_detection": (
            "ALERT" if drone["spoof_detected"] else "READY"
        ),
        "command_verification": drone["command_verification"],
        "geofence": (
            "INSIDE"
            if inside_geofence(
                drone["latitude"], drone["longitude"]
            )
            else "OUTSIDE"
        )
    }


@app.get("/")
def home():
    return jsonify({
        "project": "SkyShield",
        "backend": "running",
        "mode": "SIMULATION ONLY"
    })


@app.get("/api/health")
@limiter.limit("30 per minute")
def health():
    return jsonify({
        "status": "ok",
        "timestamp": utc_now()
    })


@app.get("/api/dashboard")
@require_api_key
def dashboard():
    return jsonify({
        "drone": drone,
        "security": security_summary(),
        "updated_at": utc_now(),
        "notice": "Simulation data only"
    })


@app.get("/api/drone/status")
@require_api_key
def drone_status():
    return jsonify(drone)


@app.post("/api/drone/connect")
@require_api_key
def connect_drone():
    drone["connection"] = "ONLINE"
    drone["authenticated"] = False
    drone["emergency_stop"] = False

    log_event("Simulated drone connected")

    return jsonify({
        "success": True,
        "drone": drone
    })


@app.post("/api/drone/disconnect")
@require_api_key
def disconnect_drone():
    drone["connection"] = "OFFLINE"
    drone["authenticated"] = False

    log_event("Drone disconnected", "WARNING")

    return jsonify({
        "success": True,
        "drone": drone
    })


@app.post("/api/drone/authenticate")
@require_api_key
def authenticate_drone():
    if drone["connection"] != "ONLINE":
        log_event("Authentication blocked: drone offline", "WARNING")
        return jsonify({
            "success": False,
            "error": "Connect the drone first"
        }), 409

    # Demo state only, not production user authentication.
    drone["authenticated"] = True
    log_event("Demo authentication successful")

    return jsonify({
        "success": True,
        "authenticated": True,
        "message": "Demo authentication verified"
    })


@app.post("/api/telemetry")
@require_api_key
@limiter.limit("30 per minute")
def update_telemetry():
    global previous_position

    payload = request.get_json(silent=True) or {}

    try:
        latitude = float(payload["latitude"])
        longitude = float(payload["longitude"])
        altitude = float(payload["altitude"])
        battery = float(payload["battery"])
        signal = float(payload["signal_strength"])
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": (
                "Provide numeric latitude, longitude, altitude, "
                "battery and signal_strength"
            )
        }), 400

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return jsonify({"error": "Invalid GPS coordinates"}), 400

    if not (0 <= altitude <= 10000):
        return jsonify({"error": "Invalid altitude"}), 400

    if not (0 <= battery <= 100 and 0 <= signal <= 100):
        return jsonify({"error": "Invalid battery or signal value"}), 400

    old_lat, old_lon = previous_position
    alerts = []

    if (
        abs(latitude - old_lat) > MAX_GPS_JUMP
        or abs(longitude - old_lon) > MAX_GPS_JUMP
    ):
        alerts.append("GPS position jump detected")

    if not inside_geofence(latitude, longitude):
        alerts.append("Geofence boundary crossed")

    if signal < MIN_SIGNAL:
        alerts.append("Low signal strength")

    drone.update({
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude,
        "battery": battery,
        "signal_strength": signal
    })

    previous_position = (latitude, longitude)

    if alerts:
        drone["spoof_detected"] = (
            "GPS position jump detected" in alerts
        )
        drone["threat_status"] = "THREAT DETECTED"
        drone["signal_integrity"] = (
            "WEAK" if signal < MIN_SIGNAL else "CHECK"
        )

        for alert in alerts:
            log_event(alert, "ALERT")
    else:
        drone["spoof_detected"] = False
        drone["threat_status"] = "PROTECTED"
        drone["signal_integrity"] = "SECURE"
        log_event("Telemetry passed basic checks")

    return jsonify({
        "success": True,
        "drone": drone,
        "alerts": alerts,
        "note": "Basic simulated checks, not real spoofing detection"
    })


@app.post("/api/security/scan")
@require_api_key
def security_scan():
    alerts = []

    if not inside_geofence(
        drone["latitude"], drone["longitude"]
    ):
        alerts.append("Outside geofence")

    if drone["signal_strength"] < MIN_SIGNAL:
        alerts.append("Low signal strength")

    if drone["spoof_detected"]:
        alerts.append("GPS anomaly flag active")

    drone["threat_status"] = (
        "THREAT DETECTED" if alerts else "PROTECTED"
    )

    log_event(
        "Security scan: " + (
            ", ".join(alerts) if alerts else "No demo alerts"
        ),
        "ALERT" if alerts else "INFO"
    )

    return jsonify({
        "success": True,
        "alerts": alerts,
        "security": security_summary()
    })


@app.post("/api/drone/command")
@require_api_key
def drone_command():
    global last_sequence

    payload = request.get_json(silent=True) or {}
    command = str(payload.get("command", "")).strip().upper()
    sequence = payload.get("sequence")

    if command not in ALLOWED_COMMANDS:
        return jsonify({"error": "Invalid command"}), 400

    if (
        not isinstance(sequence, int)
        or isinstance(sequence, bool)
        or sequence < 0
    ):
        return jsonify({
            "error": "A non-negative integer sequence is required"
        }), 400

    # Anti-replay check: old or reused sequence numbers are rejected.
    if sequence <= last_sequence:
        log_event("Replay/out-of-order command rejected", "WARNING")
        return jsonify({
            "error": "Replay or out-of-order command rejected"
        }), 409

    if drone["connection"] != "ONLINE":
        return jsonify({"error": "Drone is offline"}), 409

    if not drone["authenticated"]:
        log_event("Unauthenticated command blocked", "WARNING")
        return jsonify({"error": "Authenticate first"}), 403

    if drone["emergency_stop"] and command != "LAND":
        return jsonify({"error": "Emergency stop is active"}), 423

    if drone["spoof_detected"] and command in {
        "UP", "DOWN", "LEFT", "RIGHT"
    }:
        log_event("Movement blocked during GPS anomaly alert", "ALERT")
        return jsonify({
            "error": "Movement blocked during navigation alert"
        }), 423

    if (
        not inside_geofence(
            drone["latitude"], drone["longitude"]
        )
        and command in {"UP", "DOWN", "LEFT", "RIGHT"}
    ):
        return jsonify({
            "error": "Movement blocked outside geofence"
        }), 423

    last_sequence = sequence

    # These only change simulated telemetry.
    if command == "UP":
        drone["altitude"] = min(500, drone["altitude"] + 10)
    elif command == "DOWN":
        drone["altitude"] = max(0, drone["altitude"] - 10)
    elif command == "LEFT":
        drone["longitude"] = round(drone["longitude"] - 0.0001, 7)
    elif command == "RIGHT":
        drone["longitude"] = round(drone["longitude"] + 0.0001, 7)
    elif command == "LAND":
        drone["altitude"] = 0

    with get_db() as conn:
        conn.execute(
            """INSERT INTO commands(timestamp, sequence, command, result)
               VALUES (?, ?, ?, ?)""",
            (utc_now(), sequence, command, "SIMULATED")
        )

    log_event("Command accepted (simulated): " + command)

    return jsonify({
        "success": True,
        "command": command,
        "sequence": sequence,
        "result": "SIMULATED",
        "drone": drone
    })


@app.post("/api/drone/emergency-stop")
@require_api_key
def emergency_stop():
    drone["emergency_stop"] = True
    log_event("Emergency stop activated in simulation", "CRITICAL")

    return jsonify({
        "success": True,
        "emergency_stop": True,
        "message": "Simulation stop only; no physical drone affected"
    })


@app.get("/api/events")
@require_api_key
def events():
    limit = max(1, min(request.args.get("limit", 50, type=int), 200))

    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()

    return jsonify([dict(row) for row in rows])


@app.get("/api/commands")
@require_api_key
def command_history():
    limit = max(1, min(request.args.get("limit", 50, type=int), 200))

    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM commands ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()

    return jsonify([dict(row) for row in rows])


@app.errorhandler(404)
def not_found(_error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


init_db()
log_event("SkyShield backend started in simulation mode")

if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit(
            "Set SKYSHIELD_API_KEY before running. "
            "Do not hard-code secrets in GitHub."
        )

    app.run(host="127.0.0.1", port=5000, debug=False)
