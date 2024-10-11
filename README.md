This is Setup to work on Ubuntu 22.04. with Python 3* it may work with other distros, but untested
# GetDPD Project API Connector For The Anxiety Guy

This repository contains various Python scripts and system service files for managing and monitoring GetDPD API transactions, WordPress user additions, and service health checks for high availability and alerts.
it creats a user after a customers buys and adds them to a role you make, you need to use a wordpress plugin to lock certain programs to a role. 
## This API Integration Tool is built with 4x redundancy to ensure it is always active with clear warnings to telegram in the event of any errors

#### this works in conjunction monitoring email services, with this wordpress plugin 
https://github.com/AZBrandCanada/V1.7.19-Wordpress-Automatic-Email-Testing-With-Telegram-Alerts.git

## Contents

- `app.py`: Main program to run the application.
- `2.3wordpress.py`: Reads API logs, adds users to WordPress, and sends Telegram alerts when new users are added or when errors occur.
- `11getdpdlistsales.py`: Connects to GetDPD's API and saves transactions to `transactions.txt`.
- `monitor.py`: Checks the `timestamp.txt` file. If the file is older than 30 seconds, it sends alerts every 5 seconds to Telegram warning of an issue.
- `monitorservice.py`: Monitors all services and sends alerts if any services go down.
- `statuscheck.py`: Runs in crontab `0 4,10,22 * * * /usr/bin/python3 /home/user/The-Anxiety-Guy-GETDPD-Connector-Wordpress/statuscheck.py` and sends a Telegram status check at the specified times.
- `processed_users.txt`: Keeps a list of all users that were added to WordPress to avoid re-adding them.
- `verbosity.txt`: this is a setting file for 2.3wordpress.py, to allow sending logs to telegram whenever a new user is created.

## Installation and Usage
### 1. Clone this repository.
```
git clone https://github.com/AZBrandCanada/The-Anxiety-Guy-GETDPD-API-Connector-Wordpress.git
```
### 2. Navigate to the repository directory.
```
cd The-Anxiety-Guy-GETDPD-API-Connector-Wordpress
```
### 3. Add `wordpress`, `getdpd`, `telegram` and `SMTP` keys, `any website.ca entries in the files to your own website` and `the role for wordpres you choose to use`  to these files. 
```
nano app.py
nano 2.3wordpress.py
nano 11.getdpdlistsales.py
nano monitor.py
nano monitorservice.py
nano statuscheck.py
```

### 4. **Changing the Product to your Own Producs**
it needs to be the exact product name `only change 'VIP - Inner Circle Anxiety Recovery Program'`

   ```bash
   nano 2.3wordpressdpd.py
and edit this line 25
 vip_entries = [json.loads(line) for line in lines if 'VIP - Inner Circle Anxiety Recovery Program' in json.loads(line).get('product_name', '')]

   ```
### 5. Configure and enable the system services  
 using the provided service files below change the **`file locations`, `users` and `working directories`** to the proper ones.
 # Install System Service Files
### getdpd-service-monitor.service
```
sudo nano /etc/systemd/system/getdpd-service-monitor.service
```
```
[Service]
Type=simple
User=user
ExecStart=/usr/bin/python3 /home/user/The-Anxiety-Guy-GETDPD-API-Connector-Wordpress/monitorservice.py
WorkingDirectory=/home/user/The-Anxiety-Guy-GETDPD-Connector-Wordpress
Restart=on-failure
```

### getdpd.service
Service File Location
```
sudo nano /etc/systemd/system/getdpd.service
```
```
[Service]
Type=simple
User=user
ExecStart=/usr/bin/python3 /home/user/The-Anxiety-Guy-GETDPD-API-Connector-Wordpress/app.py
WorkingDirectory=/home/user/The-Anxiety-Guy-GETDPD-Connector-Wordpress
Restart=on-failure
```

### getdpdmonitor.service
Service File Location
```
sudo nano /etc/systemd/system/getdpdmonitor.service
```
```
[Service]
Type=simple
User=user
ExecStart=/usr/bin/python3 /home/user/The-Anxiety-Guy-GETDPD-API-Connector-Wordpress/monitor.py
WorkingDirectory=/home/user/The-Anxiety-Guy-GETDPD-API-Connector-Wordpress
Restart=on-failure
```

### emaillog.service
Service File Location
```
sudo nano /etc/systemd/system/emaillog.service
```
```
[Unit]
Description=Email Checker Service
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/emailchecker
ExecStart=/usr/bin/python3 /home/user/The-Anxiety-Guy-GETDPD-API-Connector-Wordpress/email_checker.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
```
crontab -e 
```
```
0 4,10,22 * * * /usr/bin/python3 /home/user/The-Anxiety-Guy-GETDPD-API-Connector-Wordpress/statuscheck.py
```
### 6. Ensure all required Python dependencies are installed.

### 7. Run the programs and monitor services with.
   **Reload systemd manager configuration:**
   #### After copying the service files, reload the systemd configuration to recognize the new service files.
   ```bash
   sudo systemctl daemon-reload
   ```
   #### Enable the services to start on boot.

   ```bash
   sudo systemctl enable getdpd-service-monitor.service
   sudo systemctl enable getdpd.service
   sudo systemctl enable getdpdmonitor.service
   sudo systemctl enable emaillog.service
   ```
   #### Start each service to run them immediately.

   ```bash
   sudo systemctl start getdpd-service-monitor.service
   sudo systemctl start getdpd.service
   sudo systemctl start getdpdmonitor.service
   sudo systemctl start emaillog.service
   ```

### 8. **Check the status of the services:**
   Verify that each service is running correctly.

   ```bash
   sudo systemctl status getdpd-service-monitor.service
   sudo systemctl status getdpd.service
   sudo systemctl status getdpdmonitor.service
   sudo systemctl status emaillog.service
   ```


This will ensure that the services are correctly installed, enabled, and running on your system. If there are any issues, the status command will provide details to help diagnose and fix them.


## Contributing
AZBrand.ca

## License

This project is licensed under the MIT License.





