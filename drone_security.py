from flask import Flask, jsonify

app = Flask(__name__)

drone = {
    "status": "Disconnected",
    "authenticated": False,
    "spoof_detected": False
}

@app.route("/")
def home():
    return "SkyShield - Secure Drone Control System"

@app.route("/connect")
def connect():
    drone["status"] = "Connected"
    return jsonify(drone)

@app.route("/authenticate")
def authenticate():
    drone["authenticated"] = True
    return jsonify(drone)

@app.route("/spoof-check")
def spoof_check():
    # Prototype spoof detection
    drone["spoof_detected"] = False

    if drone["spoof_detected"]:
        return jsonify({
            "alert": "Possible spoofing detected!"
        })

    return jsonify({
        "alert": "No spoofing detected"
    })


if __name__ == "__main__":
    app.run(debug=True)
