#!/bin/bash

# Define VM settings
VM_NAME="VM_LDAP"
VM_RAM_MB=8192
VM_CPUS=4
DISK_PATH="/opt/ericsson/virtualmachines/VM_CCDADM.raw"
DISK_SIZE="200G"
ISO_PATH="ubuntu-18.04.5-live-server-amd64.iso"
BRIDGE_NAME="br-om_data"

# Create disk image
qemu-img create -f raw $DISK_PATH $DISK_SIZE

# Create VM
virt-install \
    -n $VM_NAME \
    --ram $VM_RAM_MB \
    --vcpus $VM_CPUS \
    --disk $DISK_PATH \
    --network=bridge:$BRIDGE_NAME,model=virtio \
    --os-type=linux --graphics vnc,listen=0.0.0.0 --noautoconsole --os-variant=ubuntu18.04 \
    -c $ISO_PATH

echo "VM $VM_NAME created."
