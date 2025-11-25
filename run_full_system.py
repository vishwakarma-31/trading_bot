"""
Script to run both the backend and frontend of the trading bot system
"""
import subprocess
import sys
import os
import time
from threading import Thread

def run_backend():
    """Run the backend mock system"""
    print("Starting backend system...")
    try:
        # Change to the project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the mock backend
        backend_process = subprocess.Popen([
            sys.executable, 
            os.path.join('src', 'main_mock.py')
        ])
        
        print("Backend started successfully")
        backend_process.wait()
    except Exception as e:
        print(f"Error starting backend: {e}")

def run_frontend():
    """Run the Streamlit frontend"""
    print("Starting frontend UI...")
    try:
        # Change to the UI directory
        ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
        os.chdir(ui_dir)
        
        # Run the Streamlit UI on a different port to avoid conflicts
        frontend_process = subprocess.Popen([
            sys.executable, 
            '-m', 
            'streamlit', 
            'run', 
            'trading_bot_ui.py',
            '--server.port', 
            '8503'  # Changed from 8502 to 8503
        ])
        
        print("Frontend started successfully")
        frontend_process.wait()
    except Exception as e:
        print(f"Error starting frontend: {e}")

def main():
    """Main function to run both backend and frontend"""
    print("Starting Generic Trading Bot - Full System")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Give backend a moment to start
    time.sleep(2)
    
    # Start frontend in main thread
    run_frontend()
    
    print("\nSystem shutdown complete")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)