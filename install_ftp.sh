#!/bin/bash

# Install the vsftpd package
sudo apt-get update
sudo apt-get install vsftpd -y

# Configure vsftpd
sudo sed -i 's/anonymous_enable=YES/anonymous_enable=NO/' /etc/vsftpd.conf
echo "local_enable=YES" | sudo tee -a /etc/vsftpd.conf
echo "write_enable=YES" | sudo tee -a /etc/vsftpd.conf
echo "local_umask=022" | sudo tee -a /etc/vsftpd.conf
echo "chroot_local_user=YES" | sudo tee -a /etc/vsftpd.conf

# Set the FTP server root directory
echo "local_root=/home/admin/" | sudo tee -a /etc/vsftpd.conf

# Set appropriate permissions for the root directory
sudo chown root:root /home/admin/
sudo chmod 755 /home/admin

# Create the admin user
sudo useradd -m admin
echo "admin:admin" | sudo chpasswd

# Set appropriate permissions for the admin user to access the directory and download files
sudo chown -R admin:admin /home/admin
sudo chmod -R 755 /home/admin

# Restart the vsftpd service
sudo service vsftpd restart
sudo service vsftpd status

echo "FTP server installed, and admin user created."
