What’s been done:
Disabling Root Login:
Successfully disabled root login via SSH by modifying the /etc/ssh/sshd_config file and restarting the SSH service.
Key-based SSH Access:
Using key-based SSH access to connect to the EC2 instance, and root login is disabled, which adds a layer of security.
Non-root User Setup:
Confirmed that the default ec2-user already has sudo privileges, so there was no need to add a new non-root user.
Firewall Configuration (Optional):
AWS Security Groups are already configured for your EC2 instance (SSH, HTTP, HTTPS access), so opted not to configure an additional firewall (UFW).
