This is Setup to work on Ubuntu 22.04. with Python 3*
# GetDPD Project API Connector For The Anxiety Guy

This repository contains various Python scripts and system service files for managing and monitoring GetDPD API transactions, WordPress user additions, and service health checks.

## Contents

- `app.py`: Main program to run the application.
- `2.3wordpress.py`: Reads API logs, adds users to WordPress, and sends Telegram alerts when new users are added or when errors occur.
- `11getdpdlistsales.py`: Connects to GetDPD's API and saves transactions to `transactions.txt`.
- `monitor.py`: Checks the `timestamp.txt` file. If the file is older than 30 seconds, it sends alerts every 5 seconds to Telegram warning of an issue.
- `monitorservice.py`: Monitors all services and sends alerts if any services go down.
- `statuscheck.py`: Runs in crontab (`0 4,10,22 * * * /usr/bin/python3 /home/user/getdpd/statuscheck.py`) and sends a Telegram status check at the specified times.
- `processed_users.txt`: Keeps a list of all users that were added to WordPress to avoid re-adding them.
- `verbosity.txt`: Looks for the word "verbosity" and sends the logs to Telegram when a sale is made.

## Installation and Usage
### 1. Clone this repository.
```
git clone https://github.com/AZBrandCanada/THE-Anxiety-Guy-GETDPD-WORDPRESS-API-CONNECTOR.git
```
### 2. Add wordpress, getdpd telegram and SMTP keys to these files. 
```
nano app.py
nano 2.3wordpress.py
nano 11.getdpdlistsales.py
nano monitor.py
nano monitorservice.py
nano satuscheck.py
```
```
git clone https://github.com/AZBrandCanada/THE-Anxiety-Guy-GETDPD-WORDPRESS-API-CONNECTOR.git
```
### 3. Navigate to the repository directory.
```
cd THE-Anxiety-Guy-GETDPD-WORDPRESS-API-CONNECTOR
```
### 4. Configure and enable the system services  [Install System Service Files Link](https://github.com/AZBrandCanada/THE-Anxiety-Guy-GETDPD-WORDPRESS-API-CONNECTOR/blob/main/README.md#install-system-service-files)
 using the provided service files below change the file locations, users and working directories to the proper ones.
 # Install System Service Files

### getdpd-service-monitor.service
```
/etc/systemd/system/getdpd-service-monitor.service
```
```
[Service]
Type=simple
User=user
ExecStart=/usr/bin/python3 /home/user/getdpd/monitorservice.py
WorkingDirectory=/home/user/getdpd
Restart=on-failure
```

### getdpd.service
Service File Location
```
/etc/systemd/system/getdpd.service
```
```
[Service]
Type=simple
User=user
ExecStart=/usr/bin/python3 /home/user/getdpd/app.py
WorkingDirectory=/home/user/getdpd
Restart=on-failure
```

### getdpdmonitor.service
Service File Location
```
/etc/systemd/system/getdpdmonitor.service
```
```
[Service]
Type=simple
User=user
ExecStart=/usr/bin/python3 /home/user/getdpd/monitor.py
WorkingDirectory=/home/user/getdpd
Restart=on-failure
```

### emaillog.service
Service File Location
```
/etc/systemd/system/emaillog.service
```
```
[Unit]
Description=Email Checker Service
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/emailchecker
ExecStart=/usr/bin/python3 /home/user/emailchecker/email_checker.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
```
crontab -e 
```
```
0 4,10,22 * * * /usr/bin/python3 /home/user/getdpd/statuscheck.pya
```
### 5. Ensure all required Python dependencies are installed.

### 6. Run the programs and monitor services with.
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
    **Start the services:**
   #### Start each service to run them immediately.

   ```bash
   sudo systemctl start getdpd-service-monitor.service
   sudo systemctl start getdpd.service
   sudo systemctl start getdpdmonitor.service
   sudo systemctl start emaillog.service
   ```

### 7. **Check the status of the services:**
   Verify that each service is running correctly.

   ```bash
   sudo systemctl status getdpd-service-monitor.service
   sudo systemctl status getdpd.service
   sudo systemctl status getdpdmonitor.service
   sudo systemctl status emaillog.service
   ```

This will ensure that the services are correctly installed, enabled, and running on your system. If there are any issues, the status command will provide details to help diagnose and fix them.
 ```  
```

## Contributing


## License

This project is licensed under the MIT License.





