# Import libraries
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import storage
import notification

def check_and_send_alerts():
    # Get all sessions that need an alert sent
    pending_alerts = storage.get_pending_alerts()

    for session in pending_alerts:
        session_id  = session[0]
        title       = session[1]
        start_time  = session[2]

        print(f"Firing alert for: {title} at {start_time}")

        # Send the SMS alert
        result = notification.send_exercise_alert(
            child_name='Riot',
            exercise_title=title,
            start_time=start_time,
            has_cgm=False
        )

        # Log the alert in the database
        if result:
            storage.save_alert(session_id, 'SMS')
            print(f"Alert logged for session {session_id}")
        else:
            print(f"Alert failed for session {session_id}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_and_send_alerts,
        'interval',
        seconds=60
    )
    scheduler.start()
    print("Scheduler started - checking for alerts every 60 seconds.")
    return scheduler


if __name__ == '__main__':
    import time
    storage.create_tables()
    start_scheduler()
    print("Scheduler running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped.")