from flask import Flask, render_template, request, jsonify, Response
import subprocess
import signal
import os
import sys
import select

server = Flask(__name__)

loop = None

# Глобальные переменные для хранения PID процесса сканирования и атаки
scan_process = None
deauth_process = None
monitor_process = None

# Главная страница
@server.route('/')
def index():
    return render_template('index.html')

# Запуск сканирования
@server.route('/start_scan', methods=['POST'])
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
@server.route('/toggle_deauth', methods=['POST'])
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
@server.route('/toggle_monitor', methods=['POST'])
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
    
@server.route('/update_status', methods=['GET'])
def update_status():
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
    
@server.route('/stream')
def stream():
    def generate():
        while True:
            if scan_process:
                # Используем select для мониторинга stdout и stderr
                rlist, wlist, xlist = select.select([scan_process.stdout, scan_process.stderr], [], [], 0.1)
                for stream in rlist:
                    if stream == scan_process.stdout:
                        line = scan_process.stdout.readline()
                        if line:
                            yield f"data: {line}\n\n"
                    elif stream == scan_process.stderr:
                        error = scan_process.stderr.readline()
                        if error:
                            yield f"data: {error}\n\n"
            elif deauth_process:
                rlist, wlist, xlist = select.select([deauth_process.stdout, deauth_process.stderr], [], [], 0.1)
                for stream in rlist:
                    if stream == deauth_process.stdout:
                        line = deauth_process.stdout.readline()
                        if line:
                            yield f"data: {line}\n\n"
                    elif stream == deauth_process.stderr:
                        error = deauth_process.stderr.readline()
                        if error:
                            yield f"data: {error}\n\n"
            elif monitor_process:
                rlist, wlist, xlist = select.select([monitor_process.stdout, monitor_process.stderr], [], [], 0.1)
                for stream in rlist:
                    if stream == monitor_process.stdout:
                        line = monitor_process.stdout.readline()
                        if line:
                            yield f"data: {line}\n\n"
                    elif stream == monitor_process.stderr:
                        error = monitor_process.stderr.readline()
                        if error:
                            yield f"data: {error}\n\n"
            else:
                break
    return Response(generate(), mimetype='text/event-stream')

def print_ip():
    ip = subprocess.run(
        "ip -4 -o addr show | awk '$2 ~ /^en/ {print $4}' | cut -d/ -f1",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()
    if ip:
        print(f"IP-адрес интерфейса USB-Ethernet: {ip}")

if __name__ == '__main__':
    print(f"Server running on localhost:5000")
    print_ip()
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    server.run(host="0.0.0.0", port=5000)
