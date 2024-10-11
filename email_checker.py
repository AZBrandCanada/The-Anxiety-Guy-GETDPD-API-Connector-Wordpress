import os
import time
import requests
from datetime import datetime, timedelta

# List of log file URLs and corresponding website URLs
log_files = {
    "AZbrand.ca": {
        "log_url": "https://AZBrand.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://AZBrand.ca/wp-admin"
    },
    "website.ca": {
        "log_url": "https://website.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://website.ca/wp-admin"
    },
    "website.ca": {
        "log_url": "https://website.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://website.ca/wp-admin"
    },
    "website.ca": {
        "log_url": "https://website.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://website.ca/wp-admin"
    },
    "website.ca": {
        "log_url": "https://website.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://website.ca/wp-admin"
    }
}

# Telegram Bot credentials
bot_token = ""
channel_id = ""

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

def fetch_log_file(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.splitlines()
        else:
            print(f"Failed to fetch log file from {url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching log file from {url}: {e}")
        return None

def check_log_files(log_files):
    statuses = {}  # Dictionary to hold the status of each log file

    for site, info in log_files.items():
        log_url = info["log_url"]
        lines = fetch_log_file(log_url)
        if lines is not None:
            if lines:  # Check if the log file has any entries
                last_entry = lines[-1].strip()  # Get the last entry
                print(f"Last entry for {site}: {last_entry}")  # Debugging line
                last_timestamp_str = last_entry.split(']')[0][1:]  # Extract the timestamp
                print(f"Timestamp extracted for {site}: {last_timestamp_str}")  # Debugging line
                try:
                    last_timestamp = datetime.strptime(last_timestamp_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    print(f"Error parsing timestamp for {site}: {last_timestamp_str}")  # Debugging line
                    statuses[site] = "down (invalid timestamp format)"
                    continue

                # Convert last timestamp to UTC
                last_timestamp = last_timestamp.replace(tzinfo=None)  # Remove any timezone info
                
                # Check if the last entry is more than 1 hour old
                if (datetime.utcnow() - last_timestamp).total_seconds() > 28800:
                    print(f"Log {log_url} email_checker.py is older than 6 hour: {last_entry}")
                    statuses[site] = "down email_checker.py (log older than 6 hours)"
                elif "Failure" in last_entry:
                    print(f"Failure found in {log_url}: {last_entry}")
                    statuses[site] = "down (email failure)"
                else:
                    print(f"Success found in {log_url}: {last_entry}")
                    statuses[site] = "up"
            else:
                print(f"{log_url} is empty.")
                statuses[site] = "down (log is empty)"
        else:
            print(f"Could not fetch {log_url}.")
            statuses[site] = "down (fetch error)"

    return statuses  # Return the status dictionary

def send_status_update(statuses):
    status_message = "Status Update:\n"
    for site, status in statuses.items():
        status_message += f"{site}: {status}\n"
    send_telegram_message(status_message)

def visit_websites(log_files):
    for site, info in log_files.items():
        site_url = info["site_url"]
        try:
            response = requests.get(site_url)
            if response.status_code == 200:
                print(f"Successfully loaded {site_url} for {site}")
            else:
                print(f"Failed to load {site_url} for {site}: {response.status_code}")
        except Exception as e:
            print(f"Error loading {site_url} for {site}: {e}")

if __name__ == "__main__":
    # Send initial startup message
    send_telegram_message("Script has started and is now monitoring email services.")

    last_status_time = None

    while True:
        current_time = datetime.utcnow()  # Use UTC time
        
        # Send heartbeat at 5 AM and 5 PM UTC
        if current_time.hour in [5, 17] and (last_status_time is None or (current_time - last_status_time) >= timedelta(hours=1)):
            statuses = check_log_files(log_files)
            send_status_update(statuses)
            last_status_time = current_time  # Update last status time
        else:
            # Countdown until next check at 5 AM or 5 PM UTC
            next_check_time = current_time.replace(hour=5, minute=0, second=0, microsecond=0) if current_time.hour < 17 else current_time.replace(hour=17, minute=0, second=0, microsecond=0)
            if next_check_time < current_time:
                next_check_time += timedelta(days=1)
            time_until_next_check = (next_check_time - current_time).total_seconds()
            print(f"Next status update at {next_check_time.strftime('%Y-%m-%d %H:%M:%S')} (in {int(time_until_next_check // 60)} minutes and {int(time_until_next_check % 60)} seconds)")

        # Visit each website to trigger cron jobs
        visit_websites(log_files)
        print("Waiting for 4 minutes to allow crons to run...")
        time.sleep(480)  # Wait for 8 minutes

        statuses = check_log_files(log_files)
        
        # Check if there are any down statuses
        if any(status != "up" for status in statuses.values()):
            alert_message = "ALERT: One or more email services are down!\n"
            for site, status in statuses.items():
                alert_message += f"{site}: {status}\n"
            send_telegram_message(alert_message)
            time.sleep(20)  # Wait for 20 seconds before the next check
        else:
            print("All services are up. Waiting for the next check.")
            time.sleep(7200)  # Wait for an hour before checking again
