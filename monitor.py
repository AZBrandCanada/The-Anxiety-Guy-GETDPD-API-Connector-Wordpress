import time
import requests
from datetime import datetime, timedelta
from pytz import timezone, utc
import os
import sys

working_directory = '/home/user/getdpd'
os.chdir(working_directory)
print("Current working directory:", os.getcwd())
# Your Telegram bot token and chat ID

telegram_token = ''
telegram_chat_id = ''

# Function to send messages to Telegram
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Telegram message sent successfully.")
    else:
        print(f"Failed to send Telegram message. Status code: {response.status_code}, Response: {response.text}")



# Function to read the timestamp from the file and make it timezone-aware
def read_timestamp(file_path='timestamp.txt'):
    try:
        with open(file_path, 'r') as file:
            timestamp_str = file.read().strip()
            timestamp_naive = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            timestamp_aware = timezone('UTC').localize(timestamp_naive)
            return timestamp_aware
    except Exception as e:
        print(f"Error reading timestamp file {file_path}: {e}")
        return None

# Function to get the next scheduled time for status check
def get_next_scheduled_time(now, schedule_hours):
    today = now.date()
    scheduled_times = [datetime(today.year, today.month, today.day, hour, tzinfo=timezone('UTC')) for hour in schedule_hours]
    future_times = [time for time in scheduled_times if time > now]
    if future_times:
        return min(future_times)
    else:
        return min(scheduled_times) + timedelta(days=1)

# Schedule times in 24-hour format (5 AM and 5 PM)
schedule_hours = [22, 11]

# Variables to track if status check messages have been sent for the current day
status_check_sent = {hour: False for hour in schedule_hours}


message = "GETDPD Monitor Started"
print(message)
send_telegram_message(telegram_token, telegram_chat_id, message)


while True:
    now = datetime.now(timezone('UTC'))
    last_timestamp = read_timestamp()
    
    # Print the current status
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Monitoring script running...")

    # Check if the last timestamp is more than 1 minute old
    if last_timestamp:
        time_diff = now - last_timestamp
        if time_diff.total_seconds() > 30:
            while time_diff.total_seconds() > 30:
                message = "Alert: The process_user script has not updated the timestamp for over 30 seconds."
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Current time...")
                print(message)
                send_telegram_message(telegram_token, telegram_chat_id, message)
                time.sleep(5)  # Wait 5 seconds before the next check
                now = datetime.now(timezone('UTC'))
                last_timestamp = read_timestamp()
                time_diff = now - last_timestamp
        else:
            print(f"Last update was {time_diff.total_seconds()} seconds ago, no alert needed.")
    else:
        print("No valid timestamp found.")

    # Calculate the next scheduled status check time
    next_scheduled_time = get_next_scheduled_time(now, schedule_hours)

    # Countdown logic with timestamp checking
    while datetime.now(timezone('UTC')) < next_scheduled_time:
        countdown = next_scheduled_time - datetime.now(timezone('UTC'))
        #print(f"Next status check in: {str(countdown).split('.')[0]}", end='\r')

        # Check the timestamp every 5 seconds
        for _ in range(5):
            time.sleep(1)
            now = datetime.now(timezone('UTC'))
            last_timestamp = read_timestamp()
            if last_timestamp:
                time_diff = now - last_timestamp
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Last update was {time_diff.total_seconds():.2f} seconds ago. Next status check in: {str(countdown).split('.')[0]}", end='\r')
                if time_diff.total_seconds() > 30:
                    message = "Alert: The process_user script has not updated the timestamp for over 30 seconds."
                    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Current time...")
                    print(message)
                    send_telegram_message(telegram_token, telegram_chat_id, message)
                    break  # Exit the countdown if alert is triggered
        else:
            continue  # Continue the countdown if no alert was triggered
        break  # Exit the countdown loop

    # Sleep for a short time to avoid high CPU usage
    time.sleep(5)
