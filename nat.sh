#!/bin/bash
# Enable IP forwarding
echo "Enabling IP forwarding..."
echo 1 > /proc/sys/net/ipv4/ip_forward
# Configure NAT and forwarding rules for out interface
sudo iptables --table nat --append POSTROUTING --out-interface wlp0s20f3 -j MASQUERADE
sudo iptables --append FORWARD --in-interface enx00e04c68014c -j ACCEPT
sudo iptables --append FORWARD --in-interface enx00e04c68014c -j ACCEPT
# Configure NAT and forwarding rules for wlp0s20f3 interface
echo "Configuring NAT and forwarding rules for wlp0s20f3 interface..."
iptables -t nat -A POSTROUTING -o wlp0s20f3 -j MASQUERADE
iptables -A FORWARD -ienx00e04c68014c -o wlp0s20f3 -j ACCEPT
echo "Enables packet forwarding by kernel..."
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
echo "Apply the configuration..."
sudo iptables-save > /etc/sysconfig/iptables
sudo cat /etc/rc.d/rc.local
sduo  if ! grep -q "iptables-restore < /etc/sysconfig/iptables" /etc/rc.d/rc.local; then     sed -i '$a iptables-restore < /etc/sysconfig/iptables' /etc/rc.d/rc.local; fi
echo "For List the iptables rules"
sudo iptables -t nat -vnL
echo "Configuration completed."
