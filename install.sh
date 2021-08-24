#!/bin/bash

yum install -y yum-utils
yum install -y epel-release
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io mongodb python3 python3-pip snapd

systemctl enable --now snapd.socket
ln -s /var/lib/snapd/snap /snap
snap install ngrok

cp *.service /etc/systemd/system/
systemctl daemon-reload

docker run -d -p 8086:8086 -v /root/influx-data/:/var/lib/influxdb influxdb:1.8

pip3 install -r requirements.txt

systemctl enable kpy-flask-app.service
systemctl enable kpy-housekeeping.service
systemctl enable kpy-ngrok.service

systemctl start kpy-flask-app.service
echo "Installation complete. To start the app, access the web GUI through localhost:5000 and set app parameters on the Administration page."


