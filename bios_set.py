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

# Command to update firmware
commands = (
    "racadm set BIOS.MemSettings.CECriticalSEL Enabled",
    "racadm set bios.SysProfileSettings.SysProfile Custom",
    "racadm set BIOS.SysProfileSettings.CpuInterconnectBusLinkPower Disabled",
    "racadm set BIOS.SysProfileSettings.EnergyPerformanceBias MaxPower",
    "racadm set BIOS.SysProfileSettings.PcieAspmL1 Disabled",
    "racadm set BIOS.SysProfileSettings.ProcC1E Disabled",
    "racadm set BIOS.SysProfileSettings.ProcCStates Disabled",
    "racadm set BIOS.SysProfileSettings.ProcPwrPerf MaxPerf",
    "racadm set BIOS.SysProfileSettings.UncoreFrequency MaxUFS",
    "racadm set bios.SysProfileSettings.SysProfile PerfOptimized",
    "racadm set BIOS.SysSecurity.Tpm2Hierarchy Disabled",
    "racadm set BIOS.SysSecurity.TpmSecurity Off",
    "racadm set BIOS.SysProfileSettings.ProcTurboMode Disabled",
    "racadm set BIOS.SysProfileSettings.MemPatrolScrub Disabled",
    "racadm jobqueue create BIOS.Setup.1-1 -r Graceful",
    "racadm set biOS.integratedDevices.sriovGlobalEnable Enabled",
    "racadm set NIC.DeviceLevelConfig.5.VirtualizationMode SRIOV",
    "racadm set NIC.DeviceLevelConfig.7.VirtualizationMode SRIOV",
	#"racadm jobqueue create NIC.Slot.1-1-1",
    #"racadm jobqueue create NIC.Slot.2-1-1",
)

# Command to check job queue
job_queue_command = "racadm jobqueue view"

# Command to reboot
reboot_command = "racadm serveraction hardreset"

# Maximum number of retries for a command
max_retries = 3

def execute_ssh_command(ssh, command):
    retries = 0
    while retries < max_retries:
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            result = stdout.read().decode('utf-8')
            return result
        except Exception as e:
            print(f"Error executing command: {str(e)}. Retrying...")
            retries += 1
            time.sleep(5)
    return None

def process_node(ip):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)

        log_entry = f"\nNode: {ip}\n"
        print(f"Node: {ip}")

        for command in commands:
            try:
                print(f"Executing on {ip}: {command}")
                result = execute_ssh_command(ssh, command)
                if result is not None:
                    log_entry += f"Command: {command}\n"
                    log_entry += f"Result:\n{result}\n"
                    log_entry += "---------------------------\n"
                    print(f"Result:\n{result}")
                    print("---------------------------")

                    if command.startswith("racadm set"):
                        print(f"Rebooting {ip}")
                        reboot_result = execute_ssh_command(ssh, reboot_command)
                        print(reboot_result)
            except Exception as cmd_err:
                print(f"Error executing command on {ip}: {str(cmd_err)}")

        # Close the SSH connection
        ssh.close()

        # Wait for a few seconds before executing the job queue command
        time.sleep(10)

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=10)
            
            print(f"Viewing job queue on {ip}")
            job_queue_result = execute_ssh_command(ssh, job_queue_command)
            print(job_queue_result)
            ssh.close()
        except Exception as job_queue_err:
            print(f"Error viewing job queue on {ip}: {str(job_queue_err)}")

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
