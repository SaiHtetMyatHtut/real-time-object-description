import uvicorn
import signal
import sys
import subprocess
import time

def signal_handler(sig, frame):
    print("Shutting down the servers...")
    if frontend_process:
        frontend_process.terminate()
    sys.exit(0)

if __name__ == "__main__":
    # Register the signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the FastAPI backend server 
    # http://58.91.213.145:50337/
    backend_process = subprocess.Popen([
        "uvicorn", "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--ssl-keyfile", "frontend/cert/key.pem",
        "--ssl-certfile", "frontend/cert/cert.pem"
    ])
    
    # Wait for the backend to start (adjust the sleep time as needed)
    time.sleep(5)

    # Run the SvelteKit frontend server
    frontend_process = subprocess.Popen(["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "8080"], cwd="frontend")

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C
        signal_handler(signal.SIGINT, None)