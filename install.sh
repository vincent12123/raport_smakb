#!/bin/bash
# install.sh - Script instalasi untuk Raport Ortu SMA Karya Bangsa

set -e

echo "=========================================="
echo "  Installing Raport Ortu SMA Karya Bangsa"
echo "=========================================="

# Install dependencies yang diperlukan
echo "Installing required dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev build-essential

# Create app directory
APP_DIR="/opt/raport_ortu_smakb"
echo "Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR

# Copy project files
echo "Copying project files..."
sudo cp -r . $APP_DIR/
cd $APP_DIR

# Create virtual environment
echo "Creating virtual environment..."
sudo python3 -m venv venv
sudo chown -R $USER:$USER $APP_DIR

# Activate venv and install requirements
echo "Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Set permissions
echo "Setting permissions..."
sudo chown -R www-data:www-data $APP_DIR
sudo chmod +x $APP_DIR/run.py

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/raport-ortu.service > /dev/null <<EOF
[Unit]
Description=Raport Ortu SMA Karya Bangsa
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python run.py
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable raport-ortu.service

# Start the application
echo "Starting application..."
sudo systemctl start raport-ortu.service

echo ""
echo "=========================================="
echo "  Installation completed successfully!"
echo "=========================================="
echo ""
echo "Application is running on:"
echo "  - Direct access: http://$(hostname -I | awk '{print $1}'):3123"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status raport-ortu    # Check status"
echo "  sudo systemctl restart raport-ortu   # Restart app"
echo "  sudo systemctl stop raport-ortu      # Stop app"
echo "  sudo journalctl -u raport-ortu -f    # Follow logs"
echo ""