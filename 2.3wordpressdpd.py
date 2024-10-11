import time
import subprocess
import requests
from requests.auth import HTTPBasicAuth
import json
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Function to generate a random 8-character password
def generate_random_password(length=80):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Function to read all VIP+ entries from transactions.txt
def get_all_vip_entries(file_path='transactions.txt'):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
        # Filter lines to get only VIP+ entries
        vip_entries = [json.loads(line) for line in lines if 'VIP - Inner Circle Anxiety Recovery Program' in json.loads(line).get('product_name', '')]
        
        return vip_entries
    except Exception as e:
        print_verbose(f"Error reading file {file_path}: {e}")
        return []

def get_user_id(site_url, username, app_password, user_login):
    endpoint = f"{site_url}/wp-json/wp/v2/users"
    auth = HTTPBasicAuth(username, app_password)
    params = {'search': user_login}

    response = requests.get(endpoint, auth=auth, params=params)
    print_verbose(f"GET Response status code: {response.status_code}")
    print_verbose("GET Response text:")
    print_verbose(response.text)

    if response.status_code == 200:
        users = response.json()
        for user in users:
            # Check both 'slug' and 'name' to find the matching user
            if user['slug'] == user_login or user['name'] == user_login:
                return user['id']
        return None
    else:
        print_verbose(f"Failed to retrieve users. Status code: {response.status_code}, Response: {response.text}")
        return None

def add_wordpress_user(site_url, username, app_password, user_data):
    endpoint = f"{site_url}/wp-json/wp/v2/users"
    auth = HTTPBasicAuth(username, app_password)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(endpoint, auth=auth, headers=headers, data=json.dumps(user_data))
    print_verbose(f"POST Response status code: {response.status_code}")
    print_verbose("POST Response text:")
    print_verbose(response.text)

    if response.status_code == 201:
        print_verbose("User added successfully.")
        return response.json()
    else:
        print_verbose(f"Failed to add user. Status code: {response.status_code}, Response: {response.text}")
        return None

def assign_role(site_url, username, app_password, user_id, role):
    endpoint = f"{site_url}/wp-json/wp/v2/users/{user_id}"
    auth = HTTPBasicAuth(username, app_password)
    headers = {'Content-Type': 'application/json'}
    data = {'roles': [role]}
    response = requests.post(endpoint, auth=auth, headers=headers, data=json.dumps(data))
    print_verbose(f"Role Assignment Response status code: {response.status_code}")
    print_verbose("Role Assignment Response text:")
    print_verbose(response.text)

    if response.status_code == 200:
        print_verbose("User role assigned successfully.")
    else:
        print_verbose(f"Failed to assign user role. Status code: {response.status_code}, Response: {response.text}")

def save_processed_user(email, products, password, file_path='processed_users.txt'):
    try:
        with open(file_path, 'a') as file:
            file.write(f"{email} | {','.join(products)} | {password}\n")
    except Exception as e:
        print_verbose(f"Error writing to file {file_path}: {e}")

def is_user_processed(email, product, file_path='processed_users.txt'):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if email in line:
                    line_data = line.split('|')
                    if product in line_data[1].strip().split(','):
                        return True
        return False
    except FileNotFoundError:
        return False
    except Exception as e:
        print_verbose(f"Error reading file {file_path}: {e}")
        return False

def update_processed_user(email, product, file_path='processed_users.txt'):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        with open(file_path, 'w') as file:
            for line in lines:
                if email in line:
                    line_data = line.split('|')
                    products = line_data[1].strip().split(',')
                    if product not in products:
                        products.append(product)
                        line_data[1] = ','.join(products)
                    file.write('|'.join(line_data))
                else:
                    file.write(line)
    except Exception as e:
        print_verbose(f"Error updating file {file_path}: {e}")

def ensure_user_exists_and_assign_role(site_url, username, app_password, user_data, role):
    user_login = user_data['username']
    user_id = get_user_id(site_url, username, app_password, user_login)

    if user_id is None:
        print_verbose(f"User '{user_login}' does not exist. Creating user...")
        new_user = add_wordpress_user(site_url, username, app_password, user_data)
        if new_user:
            user_id = new_user['id']
            assign_role(site_url, username, app_password, user_id, role)
    else:
        print_verbose(f"User '{user_login}' exists. Assigning role...")
        assign_role(site_url, username, app_password, user_id, role)


# Function to send messages to Telegram
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

# Function to print verbose messages and send to Telegram if needed
def print_verbose(message):
    print(message)
    if verbose:
        send_telegram_message(telegram_token, telegram_chat_id, message)

# Check verbosity setting
verbose = False
try:
    with open('verbosity.txt', 'r') as file:
        if 'verbose' in file.read():
            verbose = True
except Exception as e:
    print(f"Error reading verbosity.txt: {e}")

# Your Telegram bot token and chat ID
telegram_token = ''
telegram_chat_id = ''

#EMAIL START#########################################
def send_email_with_gmail_smtp(to_email, username, password, product_name):
    smtp_server = ''
    smtp_port = 465
    smtp_username = ''  # Replace with your email address
    smtp_password = ''  # Replace with your email password

    # Create the email content
    body = f"Hello,\n\nYour account has been updated.\n\nYour {product_name} has been added.\n\nYour Username is\nUsername: {username}\n\nYou can Activate Account Here https://website.ca/lostpassword?activate=true&email={to_email}\n\nAfter Setting Your Password You Can Login Here\nhttps://website.ca/vip\n\nBest regards,\nThe Anxiety Guy"

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = f"Get Access to Your {product_name} Here"

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def process_user():
    # Run the first script
    subprocess.run(["python3", "11getdpdlistsales.py"])

    # Get all VIP+ entries
    vip_entries = get_all_vip_entries()
    if not vip_entries:
        print("No VIP+ entries found.")
        return

    # WordPress site details
    site_url = "https://website.ca"
    username = ""
    app_password = ""

    for entry in vip_entries:
        email = entry.get('email')
        product_name = entry.get('product_name')
        
        if is_user_processed(email, product_name):
            print(f"User {email} with product {product_name} already processed. Skipping.")
            continue

        # Prepare user data
        password = generate_random_password()
        user_data = {
            'username': email,
            'name': email,
            'first_name': email,
            'last_name': email,
            'email': email,
            'password': password
        }

        # Ensure user exists and assign role
        ensure_user_exists_and_assign_role(site_url, username, app_password, user_data, 'vipplus')

        # Save processed user and send email
        save_processed_user(email, [product_name], password)
        send_email_with_gmail_smtp(email, email, password, product_name)

    # Write the current date and time to the timestamp file


# Run the process_user function in a loop
while True:
    process_user()
    with open("timestamp.txt", "w") as file:
        file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    time.sleep(5)
