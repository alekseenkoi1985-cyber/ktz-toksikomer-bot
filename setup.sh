#!/bin/bash
set -e

# Fix systemd service
cat > /etc/systemd/system/ktz-bot.service << 'SERVICEEOF'
[Unit]
Description=KTZ Toksikomer Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ktz-bot
EnvironmentFile=/opt/ktz-bot/.env
ExecStart=/opt/ktz-bot/venv/bin/python3 /opt/ktz-bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo "Service file created"
systemctl daemon-reload
systemctl enable ktz-bot
echo "Done! Now set BOT_TOKEN in /opt/ktz-bot/.env and run: systemctl start ktz-bot"
