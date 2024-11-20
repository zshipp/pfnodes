# ACN Bot Systemd Service Setup

## Overview
This document details the setup and testing of the ACN Bot systemd service on an AWS EC2 instance. The service is configured to run automatically on boot and restart on failure.

## Service Configuration
The following systemd service configuration is saved at `/etc/systemd/system/acn_bot.service`:

```ini
[Unit]
Description=ACN Bot
After=network.target

[Service]
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/acn_bot
Environment=PYTHONUNBUFFERED=1
Environment=PATH=/home/ec2-user/pfnodes/acn_onboarding_bot_env/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=/opt/acn_bot
EnvironmentFile=/opt/acn_bot/.env
ExecStart=/home/ec2-user/pfnodes/acn_onboarding_bot_env/bin/python3 acn_discord_bot.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/acn_bot.log
StandardError=append:/var/log/acn_bot.error.log

[Install]
WantedBy=multi-user.target
```

## Test Results

### Auto-restart Test
The service was tested for automatic restart capability by sending a SIGKILL signal to the process. The logs show:
- Service detected the kill signal
- Automatically scheduled restart job
- Successfully restarted after the configured 10-second delay
- Maintained consistent restart behavior
- Reset restart counter on successful operation

### Boot Test
System reboot test confirmed:
- Service starts automatically on system boot
- Correct working directory and environment loaded
- Stable operation after boot
- Memory usage within expected parameters
- No startup errors

### Current Status
Final status check shows:
```
● acn_bot.service - ACN Bot
     Loaded: loaded (/etc/systemd/system/acn_bot.service; enabled; preset: disabled)
     Active: active (running)
     Main PID: 1944 (python3)
      Tasks: 3 (limit: 1113)
     Memory: 163.5M
```

## Setup Commands
For reference, here are the commands used to set up and manage the service:

```bash
# Enable service to start on boot
sudo systemctl enable acn_bot

# Start the service
sudo systemctl start acn_bot

# Check service status
sudo systemctl status acn_bot

# View service logs
sudo journalctl -u acn_bot -f
```

## Monitoring
The service logs to the following locations:
- Standard output: `/var/log/acn_bot.log`
- Error output: `/var/log/acn_bot.error.log`
- System logs: accessible via `journalctl -u acn_bot`



$ ssh -i "Accelerando_Church_Node_EC2_KeyPair.pem" ec2-user@3.25.93.138
   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'
Last login: Wed Nov 20 10:44:02 2024 from 118.210.37.229
[ec2-user@ip-172-31-14-165 ~]$ cd /opt/acn_bot
[ec2-user@ip-172-31-14-165 acn_bot]$ systemctl status acn_bot
● acn_bot.service - ACN Bot
     Loaded: loaded (/etc/systemd/system/acn_bot.service; enabled; preset: disabled)
     Active: active (running) since Wed 2024-11-20 12:45:50 UTC; 1min 0s ago
   Main PID: 1944 (python3)
      Tasks: 3 (limit: 1113)
     Memory: 163.5M
        CPU: 2.053s
     CGroup: /system.slice/acn_bot.service
             └─1944 /home/ec2-user/pfnodes/acn_onboarding_bot_env/bin/python3 acn_discord_bot.py

Nov 20 12:45:50 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Started acn_bot.service - ACN Bot.
[ec2-user@ip-172-31-14-165 acn_bot]$ cat acn_bot.service.config
[Unit]
Description=ACN Bot
After=network.target

[Service]
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/acn_bot
Environment=PYTHONUNBUFFERED=1
Environment=PATH=/home/ec2-user/pfnodes/acn_onboarding_bot_env/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=/opt/acn_bot
EnvironmentFile=/opt/acn_bot/.env
ExecStart=/home/ec2-user/pfnodes/acn_onboarding_bot_env/bin/python3 acn_discord_bot.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/acn_bot.log
StandardError=append:/var/log/acn_bot.error.log

[Install]
WantedBy=multi-user.target
[ec2-user@ip-172-31-14-165 acn_bot]$ cat acn_bot_restart_test.log
Nov 20 12:40:22 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Stopped acn_bot.service - ACN Bot.
Nov 20 12:40:22 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.648s CPU time.
Nov 20 12:40:23 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Started acn_bot.service - ACN Bot.
Nov 20 12:40:24 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Main process exited, code=exited, status=1/FAILURE
Nov 20 12:40:24 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Failed with result 'exit-code'.
Nov 20 12:40:24 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.620s CPU time.
Nov 20 12:40:34 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Scheduled restart job, restart counter is at 58.
Nov 20 12:40:34 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Stopped acn_bot.service - ACN Bot.
Nov 20 12:40:34 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.620s CPU time.
Nov 20 12:40:35 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Started acn_bot.service - ACN Bot.
Nov 20 12:40:36 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Main process exited, code=exited, status=1/FAILURE
Nov 20 12:40:36 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Failed with result 'exit-code'.
Nov 20 12:40:36 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.620s CPU time.
Nov 20 12:40:46 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Scheduled restart job, restart counter is at 59.
Nov 20 12:40:46 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Stopped acn_bot.service - ACN Bot.
Nov 20 12:40:46 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.620s CPU time.
Nov 20 12:40:46 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Started acn_bot.service - ACN Bot.
Nov 20 12:40:48 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Main process exited, code=exited, status=1/FAILURE
Nov 20 12:40:48 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Failed with result 'exit-code'.
Nov 20 12:40:48 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.581s CPU time.
Nov 20 12:40:58 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Scheduled restart job, restart counter is at 60.
Nov 20 12:40:58 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Stopped acn_bot.service - ACN Bot.
Nov 20 12:40:58 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.581s CPU time.
Nov 20 12:40:58 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Started acn_bot.service - ACN Bot.
Nov 20 12:41:00 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Main process exited, code=exited, status=1/FAILURE
Nov 20 12:41:00 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Failed with result 'exit-code'.
Nov 20 12:41:00 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.649s CPU time.
Nov 20 12:41:10 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Scheduled restart job, restart counter is at 61.
Nov 20 12:41:10 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Stopped acn_bot.service - ACN Bot.
Nov 20 12:41:10 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.649s CPU time.
Nov 20 12:41:10 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Started acn_bot.service - ACN Bot.
Nov 20 12:41:11 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Main process exited, code=exited, status=1/FAILURE
Nov 20 12:41:11 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Failed with result 'exit-code'.
Nov 20 12:41:11 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.601s CPU time.
Nov 20 12:41:21 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Scheduled restart job, restart counter is at 62.
Nov 20 12:41:21 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Stopped acn_bot.service - ACN Bot.
Nov 20 12:41:21 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.601s CPU time.
Nov 20 12:41:22 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Started acn_bot.service - ACN Bot.
Nov 20 12:41:28 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Stopping acn_bot.service - ACN Bot...
Nov 20 12:41:28 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Deactivated successfully.
Nov 20 12:41:28 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Stopped acn_bot.service - ACN Bot.
Nov 20 12:41:28 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.783s CPU time.
Nov 20 12:41:28 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Started acn_bot.service - ACN Bot.
Nov 20 12:44:38 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Main process exited, code=killed, status=9/KILL
Nov 20 12:44:38 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Failed with result 'signal'.
Nov 20 12:44:38 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.780s CPU time.
Nov 20 12:44:48 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Scheduled restart job, restart counter is at 1.
Nov 20 12:44:48 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Stopped acn_bot.service - ACN Bot.
Nov 20 12:44:48 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: acn_bot.service: Consumed 1.780s CPU time.
Nov 20 12:44:48 ip-172-31-14-165.ap-southeast-2.compute.internal systemd[1]: Started acn_bot.service - ACN Bot.
[ec2-user@ip-172-31-14-165 acn_bot]$ journalctl -u acn_bot --boot -n 50 --no-pager > acn_bot_boot_test.log
[ec2-user@ip-172-31-14-165 acn_bot]$
