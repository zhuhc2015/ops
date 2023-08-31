#!/bin/bash

# 安装BIND9 DNS服务器
echo "正在安装BIND9 DNS服务器..."
sudo apt update
sudo apt install -y bind9

# 配置BIND9
echo "正在配置BIND9 DNS服务器..."
sudo cp /etc/bind/named.conf.options /etc/bind/named.conf.options.bak

sudo sed -i 's/127.0.0.1/any/g' /etc/bind/named.conf.options

cat <<EOL | sudo tee -a /etc/bind/named.conf.local
zone "local" {
    type master;
    file "/etc/bind/zones/local.db";
};
EOL

sudo mkdir -p /etc/bind/zones

cat <<EOL | sudo tee /etc/bind/zones/local.db
\$TTL 604800
@       IN      SOA     ns.local. admin.local. (
                              1         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.local.
@       IN      A       192.168.1.1
ns      IN      A       192.168.1.1
EOL

# 重启BIND9服务
echo "正在重启BIND9服务..."
sudo service bind9 restart

echo "BIND9 DNS服务器安装和配置完成。"
