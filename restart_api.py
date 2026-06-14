import os
import subprocess
import time
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_port_owner(port):
    try:
        # Get PID of process listening on port
        result = subprocess.check_output(["lsof", "-t", f"-i:{port}"]).decode().strip()
        if result:
            pids = result.split("\n")
            for pid in pids:
                pid = pid.strip()
                if pid:
                    print(f"Terminating PID {pid} listening on port {port}...")
                    os.system(f"kill -9 {pid}")
            time.sleep(1)
    except Exception as e:
        print(f"Port {port} is already clear or lsof failed: {e}")

def start_server():
    print("Starting FastAPI Uvicorn server...")
    # Start the FastAPI server in the background
    subprocess.Popen(
        ["python3", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd="/Users/dokodo/Desktop/nebula",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    print("Server spawned in background.")

if __name__ == "__main__":
    kill_port_owner(8000)
    start_server()
