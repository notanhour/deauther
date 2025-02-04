scanTimeField.textContent = scanTimeSlider.value;

scanTimeSlider.addEventListener('input', function() {
    scanTimeField.textContent = scanTimeSlider.value;
});

const eventSource = new EventSource('/stream');
eventSource.onmessage = function(event) {
    output.textContent += event.data + "\n";
};

async function updateContext() {
    const response = await fetch('/check_status', { method: 'GET' });
    const data = await response.json();
    if (data.status == "success") {
        monitorBtn.textContent = data.in_monitor ? "Переключить на контроль" : "Переключить на мониторинг";
        deauthBtn.textContent = data.is_deauth ? "Стоп" : "Старт";
        scanBtn.disabled = !data.in_monitor || data.is_scan || data.is_deauth;
        deauthBtn.disabled = !data.in_monitor || data.is_scan;
    }
}

updateContext();
setInterval(updateContext, 500);

async function startScan() {
    output.textContent = "";
    const scanTime = document.getElementById('scanTimeField').textContent;
    const response = await fetch('/start_scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scanTime })
    });
    const data = await response.json();
}

async function toggleDeauth() {
    if (deauthBtn.textContent == "Старт") {
        output.textContent = "";
    }
    const targetNetworks = document.getElementById('targetNetworks').value;
    const targetClients = document.getElementById('targetClients').value;
    const response = await fetch('/toggle_deauth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ targetNetworks, targetClients })
    });
    const data = await response.json();
}

async function toggleMonitor() {
    output.textContent = "";
    const response = await fetch('/toggle_monitor', { method: 'POST' });
    const data = await response.json();
}