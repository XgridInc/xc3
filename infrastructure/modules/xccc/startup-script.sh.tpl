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

#Install Prometheus
sudo mkdir /etc/prometheus
cd /etc/prometheus/ && sudo touch prometheus.yml
sudo mkdir -p /data/prometheus
sudo chmod 777 /data/prometheus /etc/prometheus/*
sudo docker pull prom/prometheus
sudo docker run -d --name=prometheus -p 9090:9090 -v /etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus --config.file=/etc/prometheus/prometheus.yml


# install pushgateway
docker pull prom/pushgateway
docker run -d -p 9091:9091 --name=pushgateway prom/pushgateway
sudo cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['localhost:9091']
EOF
sudo docker restart prometheus

# Install Grafana
#sudo docker run -d --name grafana -p 3000:3000 grafana/grafana
sudo docker run -d -p 3000:3000 grafana/grafana-enterprise
