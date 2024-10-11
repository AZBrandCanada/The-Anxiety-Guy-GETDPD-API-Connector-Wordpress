import subprocess
import requests
from datetime import datetime
import time  # Import time module for sleep functionality

# Telegram Bot credentials
telegram_token = ''
telegram_chat_id = ''

# Log files and site URLs
log_files = {
    "AZbrand.ca": {
        "log_url": "https://AZBrand.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://azbrand.ca/wp-admin.php"
    },
    "website.ca": {
        "log_url": "https://website.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://website.ca/wp-admin"
    },
    "website.ca": {
        "log_url": "https://website.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://website.ca/wp-login.php"
    },
    "website.ca": {
        "log_url": "https://website.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://website.ca/wp-login.php"
    },
    "website.ca": {
        "log_url": "https://website.ca/wp-content/plugins/AutomaticEmailTesterAZBrand2/emaillog.txt",
        "site_url": "https://website.ca/wp-login.php"
    }
}

# Function to send messages to Telegram
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Telegram message sent successfully.")
    else:
        print(f"Failed to send Telegram message. Status code: {response.status_code}, Response: {response.text}")

# Function to check if a service is active
def is_service_active(service_name):
    try:
        output = subprocess.check_output(['systemctl', 'is-active', service_name], stderr=subprocess.STDOUT)
        return output.strip().decode('utf-8') == 'active'
    except subprocess.CalledProcessError:
        return False

# Function to get the status of all services
def get_services_status():
    services = ["getdpd", "getdpd-service-monitor", "getdpdmonitor", "emaillog"]
    status = {}
    for service in services:
        status[service] = "up" if is_service_active(service) else "down"
    return status

# Function to fetch and check log file status
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
    statuses = {}
    for site, info in log_files.items():
        # Navigate to the site URL
        site_url = info["site_url"]
        print(f"Accessing {site_url}...")

        # Perform a GET request to the site URL
        try:
            site_response = requests.get(site_url)
            http_status = site_response.status_code
            print(f"HTTP Status for {site_url}: {http_status}")  # Log the HTTP status

            time.sleep(60)  # Wait for 20 seconds between loading sites

            log_url = info["log_url"]
            lines = fetch_log_file(log_url)
            if lines is not None:
                if lines:
                    last_entry = lines[-1].strip()
                    # Extract the timestamp from the log entry
                    try:
                        last_timestamp_str = last_entry.split(']')[0][1:]  # Get the timestamp string
                        last_timestamp = datetime.strptime(last_timestamp_str, "%Y-%m-%d %H:%M:%S")  # Convert to datetime
                    except ValueError:
                        statuses[site] = "down (invalid timestamp format)"
                        continue

                    last_timestamp = last_timestamp.replace(tzinfo=None)
                    
                    # Check if the log is older than 6 hours
                    if (datetime.utcnow() - last_timestamp).total_seconds() > 22320:
                        statuses[site] = "down (log older than 6 hours)"
                    elif "Failure" in last_entry:
                        statuses[site] = "down (email failure)"
                    else:
                        statuses[site] = "up"
                else:
                    statuses[site] = "down (log is empty)"
            else:
                statuses[site] = "down (fetch error)"
        except requests.exceptions.RequestException as e:
            statuses[site] = f"down (exception: {e})"

    return statuses

# Main function to check services and send status
def check_services():
    while True:  # Loop indefinitely
        service_status = get_services_status()
        log_status = check_log_files(log_files)
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"Status Report ({current_time}):\n"
        
        message += "Service Statuses:\n"
        for service, state in service_status.items():
            message += f"{service}: {state}\n"
        
        message += "\nEmail Service Statuses:\n"
        for site, status in log_status.items():
            message += f"{site}: {status}\n"
        
        print(message)
        send_telegram_message(telegram_token, telegram_chat_id, message)

        break

if __name__ == "__main__":
    check_services()
