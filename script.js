let connected = false;
let authenticated = false;


/* CONNECT DRONE */

function connectDrone() {

    connected = true;

    document.getElementById("connectionStatus").innerText =
        "ONLINE";

    document.getElementById("connectionText").innerText =
        "Drone-01 connected";

    addLog("Drone-01 connected successfully", "green");

    showMessage("📡 Drone connection established.");

}


/* AUTHENTICATION */

function authenticateDrone() {

    if (!connected) {

        showMessage("⚠️ Connect the drone before authentication.");

        addLog("Authentication attempt blocked", "yellow");

        return;
    }


    authenticated = true;


    document.getElementById("authStatus").innerText =
        "VERIFIED";

    document.getElementById("authText").innerText =
        "Operator authenticated";

    document.getElementById("authenticationCheck").innerText =
        "VERIFIED";


    addLog("Operator authentication successful", "green");

    showMessage("🔐 Authentication successful.");

}


/* SECURITY SCAN */

function runSecurityScan() {

    if (!connected) {

        showMessage("⚠️ Connect the drone before running a scan.");

        return;
    }


    document.getElementById("spoofCheck").innerText =
        "SCANNING";


    showMessage("🔍 Running spoof detection scan...");


    setTimeout(function () {

        document.getElementById("spoofCheck").innerText =
            "SECURE";

        document.getElementById("threatStatus").innerText =
            "PROTECTED";

        document.getElementById("threatText").innerText =
            "No threat detected";

        document.getElementById("securityScore").innerText =
            "100%";


        addLog("Spoof detection scan completed — no threat detected", "green");

        showMessage("🛡️ Security scan complete. No spoofing detected.");

    }, 1500);

}


/* COMMANDS */

function sendCommand(command) {

    if (!connected) {

        showMessage("⚠️ Drone is offline.");

        return;
    }


    if (!authenticated) {

        showMessage("🔒 Command blocked. Authentication required.");

        addLog("Unauthorized command blocked", "yellow");

        return;
    }


    showMessage("📡 Command sent: " + command);

    addLog("Verified command: " + command, "green");


    if (command === "Forward") {

        document.getElementById("speed").innerText =
            "25 km/h";

        document.getElementById("altitude").innerText =
            "125 m";

        document.getElementById("telemetryAltitude").innerText =
            "125 m";
    }


    if (command === "Backward") {

        document.getElementById("speed").innerText =
            "15 km/h";

        document.getElementById("altitude").innerText =
            "115 m";

        document.getElementById("telemetryAltitude").innerText =
            "115 m";
    }


    if (command === "Left" || command === "Right") {

        document.getElementById("speed").innerText =
            "12 km/h";
    }

}


/* EMERGENCY STOP */

function emergencyStop() {

    document.getElementById("speed").innerText =
        "0 km/h";


    addLog("EMERGENCY STOP activated", "yellow");

    showMessage("🛑 Emergency stop activated.");

}


/* MESSAGE */

function showMessage(message) {

    document.getElementById("alertMessage").innerText =
        message;

}


/* LOG */

function addLog(message, type) {

    const logContainer =
        document.getElementById("eventLog");


    const newLog =
        document.createElement("div");

    newLog.className = "log";


    const time =
        new Date().toLocaleTimeString();


    let dotClass =
        type === "green"
            ? "green-text"
            : "yellow-text";


    newLog.innerHTML =
        `<span class="log-time">${time}</span>
         <span class="${dotClass}">●</span>
         ${message}`;


    logContainer.prepend(newLog);

}


/* CLEAR LOGS */

function clearLogs() {

    document.getElementById("eventLog").innerHTML = "";

    showMessage("📜 Event log cleared.");

}
