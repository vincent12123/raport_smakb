#!/bin/bash
# install.sh - Script instalasi untuk Raport Ortu SMA Karya Bangsa

set -e

echo "=========================================="
echo "  Installing Raport Ortu SMA Karya Bangsa"
echo "=========================================="

# Update system
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python dan pip
echo "Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Install git jika belum ada
sudo apt install -y git

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

# Create nginx configuration (optional)
if command -v nginx &> /dev/null; then
    echo "Creating nginx configuration..."
    sudo tee /etc/nginx/sites-available/raport-ortu > /dev/null <<EOF
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/app/static;
        expires 30d;
    }
}
EOF

    # Enable nginx site
    sudo ln -sf /etc/nginx/sites-available/raport-ortu /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    echo "Nginx configuration created and enabled."
fi

# Install and configure firewall (optional)
#echo "Configuring firewall..."
#sudo ufw allow 22/tcp
#sudo ufw allow 80/tcp
#sudo ufw allow 443/tcp
#sudo ufw allow 3000/tcp
#echo "y" | sudo ufw enable

# Start the application
echo "Starting application..."
sudo systemctl start raport-ortu.service

echo ""
echo "=========================================="
echo "  Installation completed successfully!"
echo "=========================================="
echo ""
echo "Application is running on:"
echo "  - Direct access: http://$(hostname -I | awk '{print $1}'):3000"
if command -v nginx &> /dev/null; then
    echo "  - Via Nginx: http://$(hostname -I | awk '{print $1}')"
fi
echo ""
echo "Useful commands:"
echo "  sudo systemctl status raport-ortu    # Check status"
echo "  sudo systemctl restart raport-ortu   # Restart app"
echo "  sudo systemctl logs raport-ortu      # View logs"
echo "  sudo journalctl -u raport-ortu -f    # Follow logs"
echo ""