""" 
Full-stack image processing application with FastAPI backend and Streamlit frontend
"""

import os
import sys
import argparse
import subprocess

# Set up environment for subprocesses
current_dir = os.path.dirname(os.path.abspath(__file__))
env = os.environ.copy()
env['PYTHONPATH'] = current_dir + ':' + env.get('PYTHONPATH', '')


def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Image Processing Application")

    parser.add_argument(
        "command",
        nargs="?",
        default="streamlit",
        choices=["backend", "frontend", "dev",
                 "production", "streamlit", "info", "test"],
        help="Command to run (default: streamlit)"
    )

    args = parser.parse_args()

    if args.command == "backend":
        print("🚀 Starting Backend...")
        subprocess.run([sys.executable, "scripts/start_backend.py"], env=env)
    elif args.command == "frontend":
        print("🎨 Starting Frontend...")
        subprocess.run([sys.executable, "scripts/start_frontend.py"], env=env)
    elif args.command == "dev":
        print("🔥 Starting Development Environment...")
        subprocess.run([sys.executable, "scripts/dev.py"], env=env)
    elif args.command == "test":
        print("🔥 Starting Test Environment...")
        subprocess.run([sys.executable, "scripts/test.py"], env=env)
    elif args.command == "production":
        print("🏭 Starting Production Environment...")
        subprocess.run([sys.executable, "scripts/production.py"], env=env)
    elif args.command == "streamlit":
        print("🚀 Starting Streamlit Deployment (Production Mode)...")
        subprocess.run(
            [sys.executable, "scripts/streamlit_deploy.py"], env=env)
    elif args.command == "info":
        print_info()
    else:
        parser.print_help()
        sys.exit(1)


def print_info():
    """Print application information"""
    print("🚀 Image Processing Application")
    print("=" * 40)
    print("Backend:  FastAPI (http://localhost:8000)")
    print("Frontend: Streamlit (http://localhost:8501)")
    print("Docs:     http://localhost:8000/docs")
    print()
    print("Commands:")
    print("  backend   - Start FastAPI backend only")
    print("  frontend  - Start Streamlit frontend only")
    print("  dev       - Start both services")
    print("  production - Start both services in production mode")
    print("  streamlit - Start Streamlit deployment (production mode)")
    print("  info      - Show this information")
    print()
    print("Quick Start:")
    print("  uv run python main.py dev")


if __name__ == "__main__":
    main()
