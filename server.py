from flask import Flask, render_template, request, jsonify, Response
import subprocess
import signal
import os
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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
    try:
        global scan_process
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
def start_deauth():
    try:
        global deauth_process
        if deauth_process is not None:
            os.kill(deauth_process.pid, signal.SIGINT)
            deauth_process = None
            return jsonify({"status": "success"})
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
    try:
        global monitor_process
        check = subprocess.run(['iw', 'dev'], capture_output=True, text=True)
        if "monitor" in check.stdout:
            monitor_process = subprocess.Popen(
                ['sudo', './monitor.sh', 'stop'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return jsonify({"status": "success"})
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
    try:
        check = subprocess.run(['iw', 'dev'], capture_output=True, text=True)
        is_monitor = "monitor" in check.stdout

        is_deauth = deauth_process is not None

        global scan_process
        if scan_process and scan_process.poll() is not None:
            scan_process = None
        is_scan = scan_process is not None

        return jsonify({
            "status": "success",
            "is_monitor": is_monitor,
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
    app.run(host='0.0.0.0', port=5000)