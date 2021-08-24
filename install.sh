#!/bin/bash

iptables -F
iptables-save > /etc/sysconfig/iptables

yum install -y yum-utils
yum install -y epel-release
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

cat <<EOF | sudo tee /etc/yum.repos.d/mongodb-org-5.0.repo
[mongodb-org-5.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/5.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-5.0.asc
EOF

yum install -y docker-ce docker-ce-cli containerd.io mongodb-org python3 python3-pip snapd

systemctl enable --now snapd.socket
ln -s /var/lib/snapd/snap /snap
snap install ngrok

cp *.service /etc/systemd/system/
systemctl daemon-reload

systemctl enable docker
systemctl enable mongod

systemctl start docker
systemctl start mongod

docker run -d -p 8086:8086 -v /root/influx-data/:/var/lib/influxdb influxdb:1.8

pip3 install -r requirements.txt

systemctl enable kpy-flask-app.service
systemctl enable kpy-housekeeping.service
systemctl enable kpy-ngrok.service

systemctl start kpy-flask-app.service
echo "Installation complete. To start the app, access the web GUI through localhost:5000 and set app parameters on the Administration page."


