#!/bin/bash

#Install docker
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update -y
sudo apt update -y
sudo apt install docker.io -y
sudo service docker start

# Install cloud custodian
sudo apt install python3-pip -y
sudo apt install python3-venv -y
sudo python3 -m venv custodian
source custodian/bin/activate
pip install c7n c7n-mailer
deactivate

#Install Prometheus
sudo docker network create --driver bridge xccc
sudo mkdir /etc/prometheus
cd /etc/prometheus/ && sudo touch prometheus.yml
sudo mkdir -p /data/prometheus
sudo chmod 777 /data/prometheus /etc/prometheus/*
sudo docker pull prom/prometheus
sudo docker run -d --name=prometheus --network=xccc -p 9090:9090 -v /etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus --config.file=/etc/prometheus/prometheus.yml


# install pushgateway
docker pull prom/pushgateway
docker run -d -p 9091:9091 --name=pushgateway --network=xccc prom/pushgateway
sudo cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['pushgateway:9091']
EOF
sudo docker restart prometheus

# Install Grafana
sudo echo "${env_file}" > /home/ubuntu/.env
sudo docker run -d -p 3000:3000 --name=grafana --network=xccc --env-file /home/ubuntu/.env grafana/grafana-enterprise
