import subprocess
import sys
import os
import argparse

def run_flask_api():
    """Run the Flask API backend"""
    print("Starting Flask API backend on port 5000...")
    subprocess.Popen([sys.executable, "app.py"])

def run_dash_app():
    """Run the Dash visualization frontend"""
    print("Starting Dash visualization app on port 8050...")
    subprocess.Popen([sys.executable, "dash_app.py"])

def main():
    parser = argparse.ArgumentParser(description="Run PharmaLens Application")
    parser.add_argument('--api-only', action='store_true', help='Run only the Flask API')
    parser.add_argument('--dash-only', action='store_true', help='Run only the Dash app')
    
    args = parser.parse_args()
    
    if args.api_only:
        run_flask_api()
    elif args.dash_only:
        run_dash_app()
    else:
        # Run both by default
        run_flask_api()
        run_dash_app()
    
    print("\nApplications are running:")
    print("- Flask API: http://localhost:5000")
    print("- Dash App: http://localhost:8050")
    print("\nPress Ctrl+C to stop all applications")
    
    try:
        # Keep the script running
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down applications...")
        sys.exit(0)

if __name__ == "__main__":
    main()