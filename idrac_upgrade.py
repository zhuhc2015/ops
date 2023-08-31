import paramiko
import re
import ipaddress
import multiprocessing
import os
import time

# SSH credentials
username = "root"
password = "calvin"
ip_list_file = "ip_list.txt"
log_dir = "logs"
firmware_name = "iDRAC-with-Lifecycle-Controller_Firmware_D92HF_WN64_6.00.30.00_A00.EXE"

# FTP information
ftp_server = "10.137.2.45"
ftp_path = "/"
ftp_user = "admin"
ftp_password = "admin"

# Command to update firmware
update_command_template = (
    f'racadm update -f {firmware_name} -u {ftp_user} -p {ftp_password} -l ftp://{ftp_server}{ftp_path}'
)

# Command to check job queue
job_queue_command = "racadm jobqueue view"

# Command to reboot
reboot_command = "racadm serveraction hardreset"

def execute_ssh_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode('utf-8')
    return result

def process_node(ip):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)

        log_entry = f"\nNode: {ip}\n"
        print(f"Node: {ip}")

        update_command = update_command_template
        result = execute_ssh_command(ssh, update_command)
        log_entry += f"Node: {ip}\n"  
        log_entry += f"Command: {update_command}\n"
        log_entry += f"Result:\n{result}\n"
        log_entry += "---------------------------\n"
        print(f"Node: {ip}") 
        print(f"Command: {update_command}")
        print(f"Result:\n{result}")
        print("---------------------------")

        # Reboot the node
        reboot_result = execute_ssh_command(ssh, reboot_command)
        print(reboot_result)

        # Close the SSH connection
        ssh.close()

        # Wait for a few seconds before executing the job queue command
        time.sleep(10)

        # Execute racadm jobqueue view
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)
        job_queue_result = execute_ssh_command(ssh, job_queue_command)
        print(job_queue_result)
        ssh.close()

        # Write the log entry
        log_path = os.path.join(log_dir, f"{ip}.log")
        with open(log_path, 'a') as log:
            log.write(log_entry)
            log.write(job_queue_result + "\n")
    except Exception as e:
        error_msg = f"Error connecting to {ip}: {str(e)}"
        print(error_msg)
        log_path = os.path.join(log_dir, f"{ip}_error.log")
        with open(log_path, 'a') as log:
            log.write(error_msg + "\n\n")

def main():
    ip_list = []
    with open(ip_list_file, 'r') as file:
        for line in file:
            ip = line.strip()
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                ipaddress.ip_address(ip)  
                ip_list.append(ip)

    os.makedirs(log_dir, exist_ok=True)  

    num_processes = min(len(ip_list), multiprocessing.cpu_count())  

    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(process_node, ip_list)

if __name__ == "__main__":
    main()
