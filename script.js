function connectDrone() {
    document.getElementById("status").innerHTML =
        "🟢 Drone Connected";
}

function authenticate() {
    document.getElementById("status").innerHTML =
        "🔐 Drone Authenticated";
}

function checkSpoofing() {
    document.getElementById("alert").innerHTML =
        "✅ No spoofing detected";
}
