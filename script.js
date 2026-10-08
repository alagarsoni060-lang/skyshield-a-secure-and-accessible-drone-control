let connected = false;
let authenticated = false;

function connectDrone() {
    connected = true;

    const status = document.getElementById("connectionStatus");
    const text = document.getElementById("connectionText");

    if (status) {
        status.innerText = "ONLINE";
    }

    if (text) {
        text.innerText = "Drone connected";
    }

    addLog("Drone connected successfully.");
    showMessage("✅ Drone connected successfully.");
}


function authenticateDrone() {

    if (!connected) {
        showMessage("⚠️ Connect the drone first.");
        return;
    }

    authenticated = true;

    const status = document.getElementById("authenticationStatus");

    if (status) {
        status.innerText = "VERIFIED";
    }

    addLog("Drone authentication successful.");
    showMessage("🔐 Drone authenticated successfully.");
}


function runSecurityScan() {

    showMessage("🔍 Running security scan...");

    addLog("Security scan started.");

    setTimeout(function () {

        const threat = document.getElementById("threatStatus");

        if (threat) {
            threat.innerText = "PROTECTED";
        }

        addLog("✅ Security scan complete - No spoofing detected.");

        showMessage("✅ Security scan complete. No spoofing detected.");

    }, 1500);
}


function sendCommand(command) {

    if (!connected) {
        showMessage("⚠️ Connect the drone first.");
        return;
    }

    if (!authenticated) {
        showMessage("🔐 Authenticate the drone first.");
        return;
    }

    addLog("Command sent: " + command);

    showMessage("🚁 Command sent: " + command);
}


function emergencyStop() {

    addLog("🚨 EMERGENCY STOP ACTIVATED.");

    showMessage("🚨 EMERGENCY STOP ACTIVATED!");
}


function showMessage(message) {

    const messageBox = document.getElementById("systemMessage");

    if (messageBox) {
        messageBox.innerText = message;
    } else {
        alert(message);
    }
}


function addLog(message) {

    const log = document.getElementById("eventLog");

    if (!log) {
        return;
    }

    const entry = document.createElement("div");

    entry.className = "log-entry";

    entry.innerHTML = `
        <span>●</span>
        <p>${message}</p>
    `;

    log.prepend(entry);
}
