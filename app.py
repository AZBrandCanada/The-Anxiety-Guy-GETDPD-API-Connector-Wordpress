import subprocess
import time
import requests
import threading
import os
import sys

working_directory = '/home/user/getdpd'
os.chdir(working_directory)
print("Current working directory:", os.getcwd())
# Your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = ''
TELEGRAM_CHAT_ID = ''

def send_telegram_message(message):
    """Sends a message to the specified Telegram chat."""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def start_subprocess():
    """Starts the original script as a subprocess and returns the process handle."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    return subprocess.Popen(['python3', '2.3wordpressdpd.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

def monitor_subprocess():
    """Monitors the original script subprocess and restarts it if it crashes."""
    first_start = True

    while True:
        process = start_subprocess()

        if first_start:
            start_message = "GETDPD Backend Started"
            print(start_message)
            send_telegram_message(start_message)
            first_start = False

        def log_output(stream, log_type):
            for line in iter(stream.readline, ''):
                print(f'[{log_type}] {line}', end='')

        stdout_thread = threading.Thread(target=log_output, args=(process.stdout, 'STDOUT'))
        stderr_thread = threading.Thread(target=log_output, args=(process.stderr, 'STDERR'))

        stdout_thread.start()
        stderr_thread.start()

        stdout_thread.join()
        stderr_thread.join()

        if process.returncode != 0:
            error_message = f"Script exited with error. Restarting...\nError: {process.stderr.read()}"
            print(error_message)
            send_telegram_message(error_message)
        else:
            normal_message = "Script exited normally. Restarting..."
            print(normal_message)
            send_telegram_message(normal_message)

        time.sleep(5)  # Add a delay before restarting to avoid rapid restart loops

if __name__ == "__main__":
    monitor_subprocess()
