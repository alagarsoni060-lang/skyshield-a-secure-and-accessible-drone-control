let connected = false;
let authenticated = false;
let scanning = false;


// CONNECT DRONE
function connectDrone() {

    connected = true;

    document.getElementById("connectionStatus").textContent = "ONLINE";
    document.getElementById("connectionText").textContent =
        "Drone connected successfully";

    addLog("Drone connected successfully.");

    showMessage("✅ Drone connected successfully.");
}


// AUTHENTICATE
function authenticateDrone() {

    if (!connected) {

        showMessage("⚠️ Please connect the drone first.");

        addLog("Authentication failed: drone not connected.");

        return;
    }

    authenticated = true;

    document.getElementById("authenticationStatus").textContent =
        "VERIFIED";

    document.getElementById("authCheck").textContent =
        "VERIFIED";

    addLog("Drone authentication successful.");

    showMessage("🔐 Drone authentication successful.");
}


// SECURITY SCAN
function runSecurityScan() {

    if (scanning) {
        return;
    }

    scanning = true;

    const button = document.querySelector(".scan-button");

    button.textContent = "🔄 SCANNING...";

    document.getElementById("spoofCheck").textContent =
        "SCANNING";

    document.getElementById("securityScore").textContent =
        "CHECK";

    addLog("Security scan started.");

    showMessage("🔍 Running anti-spoofing security scan...");


    setTimeout(function () {

        document.getElementById("spoofCheck").textContent =
            "CLEAR";

        document.getElementById("securityScore").textContent =
            "100%";

        document.getElementById("threatStatus").textContent =
            "PROTECTED";

        document.getElementById("threatText").textContent =
            "No spoofing detected";

        button.textContent =
            "🛡️ RUN SECURITY SCAN";

        scanning = false;

        addLog("Security scan complete. No spoofing detected.");

        showMessage(
            "✅ Security scan complete. No spoofing detected."
        );

    }, 2000);
}


// DRONE COMMAND
function sendCommand(command) {

    if (!connected) {

        showMessage("⚠️ Connect the drone first.");

        addLog(
            "Command blocked: drone is not connected."
        );

        return;
    }


    if (!authenticated) {

        showMessage("🔐 Authenticate the drone first.");

        addLog(
            "Command blocked: authentication required."
        );

        return;
    }


    addLog(
        "Verified command sent: " + command
    );

    showMessage(
        "🚁 Command executed: " + command
    );


    if (command === "LAND") {

        document.getElementById("altitude").textContent =
            "0 m";

    } else if (command === "UP") {

        document.getElementById("altitude").textContent =
            "150 m";

    } else if (command === "DOWN") {

        document.getElementById("altitude").textContent =
            "100 m";
    }
}


// EMERGENCY STOP
function emergencyStop() {

    addLog(
        "🚨 EMERGENCY STOP ACTIVATED."
    );

    showMessage(
        "🚨 EMERGENCY STOP ACTIVATED!"
    );
}


// SHOW MESSAGE
function showMessage(message) {

    const box =
        document.getElementById("systemMessage");

    box.textContent = message;
}


// EVENT LOG
function addLog(message) {

    const log =
        document.getElementById("eventLog");

    const entry =
        document.createElement("div");

    entry.className = "log";

    entry.innerHTML = `
        <span>●</span>
        <p>${message}</p>
    `;

    log.prepend(entry);
}


// CLEAR LOGS
function clearLogs() {

    document.getElementById("eventLog").innerHTML = "";

    showMessage("Event log cleared.");
}
