# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#!/bin/bash
# This script installs Docker, Cloud Custodian, Prometheus, and Grafana
# on a Linux system. It pulls the necessary Docker images, creates a bridge network,
# and writes configuration files for Prometheus and Grafana.
# The script also creates content and plugins directories for Grafana
# and sets up an environment file.

#Install docker
# Check if Docker is installed
if [ -x "$(command -v docker)" ]; then
    echo "Docker is already installed"
else
    sudo apt-get remove docker docker-engine docker.io containerd runc
    sudo apt-get update -y
    sudo apt install docker.io -y
    sudo service docker start
    if [ -x "$(command -v docker)" ]; then
        echo "Docker installed successfully"
    else
        echo "Error installing Docker"
        exit 1
    fi
fi


# Install cloud custodian
if  sudo apt install python3-pip -y
    sudo apt install python3-venv -y
    sudo python3 -m venv custodian
    source custodian/bin/activate
    pip install c7n c7n-mailer
    deactivate
then
    echo "cloud custodian installed successfully"
else
    echo "Failed to install cloud custodian"
fi


#Install Prometheus
if  sudo docker network create --driver bridge xc3
    sudo mkdir /etc/prometheus
    cd /etc/prometheus/ && sudo touch prometheus.yml
    sudo mkdir -p /data/prometheus
    sudo chmod 777 /data/prometheus /etc/prometheus/*
    sudo docker pull prom/prometheus
    sudo docker run -d --name=prometheus --network=xc3 -p 9090:9090 -v /etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus --config.file=/etc/prometheus/prometheus.yml
then
    echo "Prometheus installed successfully"
else
    echo "Failed to install Prometheus"
fi


if  docker pull prom/pushgateway
then
    echo "Successfully pulled docker image for pushgateway"
else
    echo "Failed to pull docker image for pushgateway

if  docker run -d -p 9091:9091 --name=pushgateway --network=xc3 prom/pushgateway
then
    echo "Successfully started pushgateway container"
else
    echo "Failed to start pushgateway container"


# Write the Prometheus config file
if ! sudo cat > /etc/prometheus/prometheus.yml << EOF
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
then
  echo "Error writing Prometheus config file!" >&2
  exit 1
fi

echo "Pushgateway installed and configured successfully!"

# Restart Prometheus to apply the new config file
if ! sudo docker restart prometheus
then
  echo "Error restarting Prometheus!" >&2
fi

# Write environment file to home directory
if ! sudo echo "${env_file}" > /home/ubuntu/.env
then
  echo "Error writing environment file!" >&2
fi

# Write dashboard and datasource files to home directory
if ! sudo echo "${dashboard}" > /home/ubuntu/dashboard.yml
then
  echo "Error writing dashboard file!" >&2
fi

if ! sudo echo "${datasource}" > /home/ubuntu/datasource.yml
then
  echo "Error writing datasource file!" >&2
fi

# Create content and plugins directories
if ! sudo mkdir ~/content
then
  echo "Error creating content directory!" >&2
fi

if ! sudo mkdir ~/plugins
then
  echo "Error creating plugins directory!" >&2
fi

echo "Pushgateway installed and configured successfully!"

if ! [ -x "$(command -v docker)" ]; then
  echo "Error: Docker is not installed." >&2
fi

if ! docker ps | grep -q grafana; then
    sudo docker run -d -p 3000:3000 --name grafana --network xc3 --env-file /home/ubuntu/.env \
        -e "GF_INSTALL_PLUGINS=marcusolsson-dynamictext-panel" \
        -e "GF_DEFAULT_HOME_DASHBOARD=LQ93m_o4z" \
        -v ~/content/:/var/lib/grafana/dashboards \
        -v ~/dashboard.yml:/etc/grafana/provisioning/dashboards/dashboard.yml \
        -v ~/datasource.yml:/etc/grafana/provisioning/datasources/datasources.yml \
        grafana/grafana-enterprise
else
    echo "Grafana container is already running"
fi
if [ $? -ne 0 ]; then
  echo "Error: failed to start Grafana container." >&2
  exit 1
fi
