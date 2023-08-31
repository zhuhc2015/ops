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

# Command to get BIOS settings
commands = (
    "racadm get BIOS.MemSettings.CECriticalSEL",
    "racadm get bios.SysProfileSettings.SysProfile",
    "racadm get BIOS.SysProfileSettings.CpuInterconnectBusLinkPower",
    "racadm get BIOS.SysProfileSettings.EnergyPerformanceBias",
    "racadm get BIOS.SysProfileSettings.PcieAspmL1",
    "racadm get BIOS.SysProfileSettings.ProcC1E",
    "racadm get BIOS.SysProfileSettings.ProcCStates",
    "racadm get BIOS.SysProfileSettings.ProcPwrPerf",
    "racadm get BIOS.SysProfileSettings.UncoreFrequency",
    "racadm get bios.SysProfileSettings.SysProfile",
    "racadm get BIOS.SysSecurity.Tpm2Hierarchy",
    "racadm get BIOS.SysSecurity.TpmSecurity",
    "racadm get BIOS.SysProfileSettings.MemPatrolScrub"
    "rcadm  get BIOS.SysProfileSettings.ProcTurboMode"
    "racadm get NIC.DeviceLevelConfig.5.VirtualizationMode"
    "racadm get NIC.DeviceLevelConfig.7.VirtualizationMode"
)


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

        for command in commands:
            print(f"Executing on {ip}: {command}")
            result = execute_ssh_command(ssh, command)
            log_entry += f"Command: {command}\n"
            log_entry += f"Result:\n{result}\n"
            log_entry += "---------------------------\n"
            print(f"Result:\n{result}")
            print("---------------------------")

        # Write the log entry
        log_path = os.path.join(log_dir, f"{ip}.log")
        with open(log_path, 'a') as log:
            log.write(log_entry)
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
