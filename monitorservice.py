import time
import subprocess
import requests
from datetime import datetime, timedelta

# Function to send messages to Telegram
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Telegram message sent successfully.")
    else:
        print(f"Failed to send Telegram message. Status code: {response.status_code}, Response: {response.text}")

# Your Telegram bot token and chat ID
telegram_token = ''
telegram_chat_id = ''

# Function to check if a service is active
def is_service_active(service_name):
    try:
        output = subprocess.check_output(['systemctl', 'is-active', service_name], stderr=subprocess.STDOUT)
        return output.strip().decode('utf-8') == 'active'
    except subprocess.CalledProcessError:
        return False

# Function to get the next scheduled time for the report
def get_next_report_time():
    now = datetime.utcnow()
    return now + timedelta(hours=12)

# Main function to monitor services and send updates
def monitor_services():
    last_report_time = get_next_report_time()

    while True:
        # Check service status every 60 seconds
        getdpd_status = "up" if is_service_active("getdpd") else "down"
        getdpd_monitor_status = "up" if is_service_active("getdpdmonitor") else "down"
        emaillog_status = "up" if is_service_active("emaillog") else "down"  # Check emaillog status

        # Immediate alert if any service is down
        if getdpd_status == "down" or getdpd_monitor_status == "down" or emaillog_status == "down":
            message = f"ALERT: One or more services are down!\nGetDPD: {getdpd_status}\nGetDPD Monitor: {getdpd_monitor_status}\nEmail Log: {emaillog_status}"
            print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Sending immediate alert...")
            send_telegram_message(telegram_token, telegram_chat_id, message)

        # Check if it's time for the 12-hour report
        if datetime.utcnow() >= last_report_time:
            report_message = f"Service Status Report:\nGetDPD: {getdpd_status}\nGetDPD Monitor: {getdpd_monitor_status}\nEmail Log: {emaillog_status}"
            print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Sending 12-hour status report...")
            send_telegram_message(telegram_token, telegram_chat_id, report_message)
            last_report_time = get_next_report_time()  # Reset the report time

        print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Current status - GetDPD: {getdpd_status}, GetDPD Monitor: {getdpd_monitor_status}, Email Log: {emaillog_status}")
        time.sleep(30)  # Wait for 60 seconds before the next check

if __name__ == "__main__":
    monitor_services()
