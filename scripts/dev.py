#!/usr/bin/env python3
"""
Development script to start both backend and frontend
"""
import sys
import time
import signal
import subprocess
from multiprocessing import Process


def start_backend():
    """Start backend in a separate process"""
    subprocess.run([sys.executable, "scripts/start_backend.py"])


def start_frontend():
    """Start frontend in a separate process"""
    # Wait a bit for backend to start
    time.sleep(3)
    subprocess.run([sys.executable, "scripts/start_frontend.py"])


def main():
    """Start both backend and frontend"""
    print("🚀 Starting Image Processing Application Development Environment")
    print("=" * 50)

    # Start backend process
    backend_process = Process(target=start_backend)
    backend_process.start()

    # Start frontend process
    frontend_process = Process(target=start_frontend)
    frontend_process.start()

    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.join()
        frontend_process.join()
        sys.exit(0)

    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Wait for processes
        backend_process.join()
        frontend_process.join()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
