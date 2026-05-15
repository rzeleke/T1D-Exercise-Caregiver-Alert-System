# Main entry point - starts Streamlit and the background scheduler together
import threading
import subprocess
import sys
import storage
import scheduler

def run_streamlit():
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == '__main__':
    # Step 1 - ensure database tables exist
    storage.create_tables()
    print("Database initialized.")

    # Step 2 - start the background alert scheduler
    sched = scheduler.start_scheduler()
    print("Background scheduler started.")

    # Step 3 - start Streamlit in a separate thread
    print("Starting Streamlit dashboard...")
    streamlit_thread = threading.Thread(target=run_streamlit)
    streamlit_thread.daemon = True
    streamlit_thread.start()

    print("T1D Alert System is running.")
    print("Open your browser at http://localhost:8501")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        sched.shutdown()
        print("T1D Alert System stopped.")