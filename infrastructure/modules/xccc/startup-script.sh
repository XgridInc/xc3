#!/bin/bash

#Install docker and docker compose
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update -y
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo chmod a+r /etc/apt/keyrings/docker.gpg
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
sudo service docker start
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install cloud custodian
sudo apt install python3-pip -y
sudo apt install python3-venv -y
sudo python3 -m venv custodian
source custodian/bin/activate
pip install c7n c7n-mailer
deactivate

#Install prometheus/grafana/pushgateway
export ADMIN_USER=${username}
export ADMIN_PASSWORD=${password}
git clone https://github.com/Einsteinish/Docker-Compose-Prometheus-and-Grafana.git
cd Docker-Compose-Prometheus-and-Grafana
sudo docker-compose up -d
