Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
cloud_final_modules:
- [scripts-user, always]

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
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
# This script installs Docker, Cloud Custodian, Prometheus, and Grafana
# on a Linux system. It pulls the necessary Docker images, creates a bridge network,
# and writes configuration files for Prometheus and Grafana.
# The script also creates content and plugins directories for Grafana
# and sets up an environment file.


# Install docker
# Check if Docker is installed
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update -y
sudo apt install docker.io -y
sudo service docker start
if command -v docker &> /dev/null
then
    echo "Docker installed successfully"
else
    echo "Failed to install docker"
    exit 1
fi


# Install cloud custodian
sudo apt-get install python3-pip -y
sudo apt-get install python3-venv -y

python3 -m venv custodian
source /custodian/bin/activate
pip install c7n
pip install c7n-mailer
deactivate


#Install Prometheus
if sudo docker network create --driver bridge xc3; then
    sudo mkdir /etc/prometheus
    cd /etc/prometheus/ && sudo touch prometheus.yml
    sudo mkdir -p /data/prometheus
    sudo chmod 777 /data/prometheus /etc/prometheus/*
    sudo docker pull prom/prometheus
    sudo docker run -d --name=prometheus --network=xc3 -p 9090:9090 -v /etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus --config.file=/etc/prometheus/prometheus.yml
    echo "Prometheus installed successfully"
else
    echo "Failed to install Prometheus"
fi


# Create pushgateway container
if sudo docker pull prom/pushgateway
then
    echo "Successfully pulled docker image for pushgateway"
else
    echo "Failed to pull docker image for pushgateway"
fi


if sudo docker run -d -p 9091:9091 --name=pushgateway --network=xc3 prom/pushgateway
then
    echo "Successfully started pushgateway container"
else
    echo "Failed to start pushgateway container"
fi

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


# Create content directory
if ! sudo mkdir /home/ubuntu/content
then
  echo "Error creating content directory!" >&2
fi

sudo apt install awscli -y

sudo aws s3 cp s3://${s3_bucket}/content/ /home/ubuntu/content --recursive

# Coping cloud_custodian_policies folder from S3 bucket
sudo aws s3 cp s3://${s3_bucket}/cloud_custodian_policies/ /home/ubuntu/cloud_custodian_policies/ --recursive --exclude "*.md" --include "*"

# Changing the ownership of files
sudo chown root:root /home/ubuntu/cloud_custodian_policies/msg_templates/*.html.j2

# Getting the python version from the Host machine
python_version="python$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"

# Copying files to the cloud_custodian directory
sudo cp /home/ubuntu/cloud_custodian_policies/msg_templates/*.html.j2 "/custodian/lib/$python_version/site-packages/c7n_mailer/msg-templates/"

echo "Pushgateway installed and configured successfully!"

# pragma: allowlist secret
if sudo docker run -d -p 3000:3000 --name grafana --network xc3 --env-file /home/ubuntu/.env -e "GF_INSTALL_PLUGINS=marcusolsson-dynamictext-panel" \
        -e "GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/var/lib/grafana/dashboards/home-dashboard.json" \
        -e "GRAFANA_API_GATEWAY=${grafana_api_gateway}" \
        -e "GRAFANA_REGION=${region}" \
        -v /home/ubuntu/content/:/var/lib/grafana/dashboards \
        -v /home/ubuntu/dashboard.yml:/etc/grafana/provisioning/dashboards/dashboard.yml \
        -v /home/ubuntu/datasource.yml:/etc/grafana/provisioning/datasources/datasource.yml \
        grafana/grafana-enterprise;
then
    echo "Grafana container started successfully."
else
    echo "Error: failed to start Grafana container."
    echo "Error: failed to start Grafana container."
fi

if [ $? -ne 0 ]; then
  echo "Error: failed to start Grafana container." >&2
  exit 1
fi


# Triggering XC3 lambda functions.

source /custodian/bin/activate

cd /home/ubuntu/cloud_custodian_policies

custodian run -s s3://${s3_bucket}/iam-user --region ${region} iam-user.yml

custodian run -s s3://${s3_bucket}/iam-role/ --region ${region} iam-role.yml

custodian run -s tagging-compliance --region ${region} eks-tagging.yml

--//--
