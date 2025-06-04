#!/bin/bash
# uninstall.sh - Script untuk menghapus instalasi

echo "Removing Raport Ortu SMA Karya Bangsa..."

# Stop and disable service
sudo systemctl stop raport-ortu.service
sudo systemctl disable raport-ortu.service

# Remove service file
sudo rm -f /etc/systemd/system/raport-ortu.service
sudo systemctl daemon-reload

# Remove nginx configuration
sudo rm -f /etc/nginx/sites-available/raport-ortu
sudo rm -f /etc/nginx/sites-enabled/raport-ortu
sudo systemctl reload nginx 2>/dev/null || true

# Remove application directory
sudo rm -rf /opt/raport_ortu_smakb

echo "Uninstallation completed."