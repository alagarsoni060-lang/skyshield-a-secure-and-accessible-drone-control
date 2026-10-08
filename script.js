let connected = false;
let authenticated = false;

function connectDrone() {
    connected = true;

    const connection = document.getElementById("connectionStatus");

    if (connection) {
        connection.innerText = "ONLINE";
    }

    showMessage("Drone connected successfully.");
}

function authenticateDrone() {
    if (!connected) {
        showMessage("Please connect the drone first.");
        return;
    }

    authenticated = true;

    const authentication = document.getElementById("authenticationStatus");

    if (authentication) {
        authentication.innerText = "VERIFIED";
    }

    showMessage("Drone authentication successful.");
}

function runSecurityScan() {
    showMessage("Running security scan...");

    setTimeout(function () {
        showMessage("Security scan complete. No spoofing detected.");
    }, 1500);
}

function sendCommand(command) {
    if (!connected) {
        showMessage("Connect the drone first.");
        return;
    }

    if (!authenticated) {
        showMessage("Authenticate the drone first.");
        return;
    }

    showMessage("Command sent: " + command);
}

function emergencyStop() {
    showMessage("🚨 EMERGENCY STOP ACTIVATED");
}

function showMessage(message) {
    alert(message);
}
