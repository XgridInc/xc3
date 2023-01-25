#!/bin/bash
sudo apt-get update -y
sudo apt-get install python3-pip -y
sudo apt install python3.8-venv -y
python3 -m venv custodian
source custodian/bin/activate
pip install c7n c7n-mailer
deactivate


# Install Grafana
cd ..
sudo apt-get install -y apt-transport-https
sudo apt-get install -y software-properties-common wget
sudo wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key

echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com beta main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update

# Install the latest OSS release:
sudo apt-get install grafana

# Start the server with systemd
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl status grafana-server

# Configuring the Grafana server to start at boot
sudo systemctl enable grafana-server.service
