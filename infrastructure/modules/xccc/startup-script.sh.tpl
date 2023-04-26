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

sudo echo "${env_file}" > /home/ubuntu/.env

sudo echo "${dashboard}" > /home/ubuntu/dashboard.yml
sudo echo "${datasource}" > /home/ubuntu/datasource.yml

sudo mkdir ~/content
sudo mkdir ~/plugins

if ! [ -x "$(command -v docker)" ]; then
  echo "Error: Docker is not installed." >&2
  exit 1
fi
if ! docker ps | grep -q grafana; then
    sudo docker run -d -p 3000:3000 --name grafana --network xccc --env-file /home/ubuntu/.env \
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