"""
Main entry point for the Generic Trading Bot
"""
import sys
import os
from dotenv import load_dotenv

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

from application.app_controller import ApplicationController

def main():
    """Main entry point for the application"""
    app_controller = ApplicationController()
    
    try:
        # Start the application
        success = app_controller.start()
        
        if not success:
            print("Failed to start the application")
            return 1
            
        # Keep the application running
        while app_controller.is_running():
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
        app_controller.stop()
    except Exception as e:
        print(f"Unexpected error: {e}")
        app_controller.stop()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
