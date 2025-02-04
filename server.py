from flask import Flask, render_template, request, jsonify, Response
import subprocess
import signal
import os
import sys

app = Flask(__name__)

# Глобальные переменные для хранения PID процесса сканирования и атаки
scan_process = None
deauth_process = None
monitor_process = None

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Запуск сканирования
@app.route('/start_scan', methods=['POST'])
def start_scan():
    global scan_process
    try:
        data = request.json
        scan_time = data.get('scanTime', '20')
        # Запуск bash-скрипта в асинхроне
        scan_process = subprocess.Popen(
            ['sudo', './wifi.sh', '-m', 'scan', '-t', scan_time],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error"})

# Атака
@app.route('/toggle_deauth', methods=['POST'])
def toggle_deauth():
    global deauth_process
    try:
        if deauth_process is not None:
            os.kill(deauth_process.pid, signal.SIGINT)
            deauth_process = None
        else:
            data = request.json
            target_networks = data.get('targetNetworks', '')
            target_clients = data.get('targetClients', '')
            # Запуск bash-скрипта в асинхроне
            deauth_process = subprocess.Popen(
                ['sudo', './wifi.sh', '-m', 'deauth', '-n', target_networks, '-c', target_clients],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error"})
    
# Переключение monitor mode
@app.route('/toggle_monitor', methods=['POST'])
def toggle_monitor():
    global monitor_process
    try:
        check = subprocess.run(['iw', 'dev'], capture_output=True, text=True)
        if "monitor" in check.stdout:
            monitor_process = subprocess.Popen(
                ['sudo', './monitor.sh', 'stop'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        else:
            monitor_process = subprocess.Popen(
                ['sudo', './monitor.sh', 'start'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error"})
    
@app.route('/check_status', methods=['GET'])
def check_status():
    global scan_process, deauth_process, monitor_process
    try:
        check = subprocess.run(['iw', 'dev'], capture_output=True, text=True)
        in_monitor = "monitor" in check.stdout

        is_scan = scan_process is not None and scan_process.poll() is None
        if not is_scan:
            scan_process = None

        is_deauth = deauth_process is not None and deauth_process.poll() is None
        if not is_deauth:
            deauth_process = None

        if monitor_process is not None and monitor_process.poll() is not None:
            monitor_process = None
        
        return jsonify({
            "status": "success",
            "in_monitor": in_monitor,
            "is_deauth": is_deauth,
            "is_scan": is_scan
        })
    except Exception as e:
        return jsonify({"status": "error"})
    
@app.route('/stream')
def stream():
    def generate():
        while True:
            if deauth_process:
                line = deauth_process.stdout.readline()
                if line:
                    yield f"data: {line}\n\n"
            elif scan_process:
                line = scan_process.stdout.readline()
                if line:
                    yield f"data: {line}\n\n"
            elif monitor_process:
                line = monitor_process.stdout.readline()
                if line:
                    yield f"data: {line}\n\n"
            else:
                break  
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print(f"Server running on localhost:5000")
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    app.run(host='0.0.0.0', port=5000)