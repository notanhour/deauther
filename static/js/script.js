scanTimeSlider.addEventListener('input', function() {
    scanTimeInput.value = scanTimeSlider.value;
});

scanTimeInput.addEventListener('input', function() {
    let value = parseInt(scanTimeInput.value);
    if (value > 60) {
        scanTimeInput.value = 60;
    } else if (value < 5) {
        scanTimeInput.value = 5;
    }
    scanTimeSlider.value = value;
});

const eventSource = new EventSource('/stream');
eventSource.onmessage = function(event) {
    output.textContent += event.data + "\n";
};

async function updateContext() {
    const response = await fetch('/check_status', { method: 'GET' });
    const data = await response.json();
    if (data.status == "success") {
        monitorBtn.textContent = data.is_monitor ? "Переключить в managed mode" : "Переключить в monitor mode";
        deauthBtn.textContent = data.is_deauth ? "Стоп" : "Начать атаку";
        scanBtn.disabled = data.is_scan;
    }
}

updateContext();
setInterval(updateContext, 1000);

async function startScan() {
    output.textContent = "";
    const scanTime = document.getElementById('scanTimeInput').value;
    const response = await fetch('/start_scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scanTime })
    });
    const data = await response.json();
}

async function toggleDeauth() {
    if (deauthBtn.textContent == "Начать атаку") {
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