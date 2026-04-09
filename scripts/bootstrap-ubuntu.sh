#!/bin/sh
set -e
sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt install -y git curl ca-certificates ufw fail2ban unattended-upgrades openssl chrony logrotate certbot python3-certbot-nginx docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl enable certbot.timer || true
sudo systemctl start certbot.timer || true
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban
sudo systemctl enable chrony || true
sudo systemctl start chrony || sudo systemctl start chronyd || true
sudo timedatectl set-ntp true || true
sudo install -d -m 755 /etc/ssh/sshd_config.d
printf '%s\n' 'PasswordAuthentication no' 'PermitRootLogin no' 'PubkeyAuthentication yes' 'KbdInteractiveAuthentication no' 'MaxAuthTries 3' 'LoginGraceTime 30' 'X11Forwarding no' 'AllowTcpForwarding no' 'AllowAgentForwarding no' 'PermitEmptyPasswords no' 'ClientAliveInterval 300' 'ClientAliveCountMax 2' 'UseDNS no' | sudo tee /etc/ssh/sshd_config.d/99-cluemap-hardening.conf >/dev/null
sudo systemctl restart ssh || sudo systemctl restart sshd
printf '%s\n' '[sshd]' 'enabled = true' 'maxretry = 5' 'findtime = 10m' 'bantime = 1h' | sudo tee /etc/fail2ban/jail.d/cluemap-sshd.local >/dev/null
sudo systemctl restart fail2ban
sudo install -d -m 755 /etc/systemd/journald.conf.d
printf '%s\n' '[Journal]' 'SystemMaxUse=200M' 'RuntimeMaxUse=100M' 'MaxRetentionSec=7day' | sudo tee /etc/systemd/journald.conf.d/cluemap.conf >/dev/null
sudo systemctl restart systemd-journald
sudo install -d -m 755 /etc/docker
printf '%s\n' '{' '  "live-restore": true,' '  "userland-proxy": false,' '  "log-driver": "json-file",' '  "log-opts": {' '    "max-size": "10m",' '    "max-file": "3"' '  }' '}' | sudo tee /etc/docker/daemon.json >/dev/null
sudo systemctl restart docker
sudo usermod -aG docker "$USER"
sudo mkdir -p /opt/cluemap /opt/cluemap/backups /opt/cluemap/infra/nginx/certs
sudo chown -R "$USER":"$USER" /opt/cluemap
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw limit OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
sudo dpkg-reconfigure -f noninteractive unattended-upgrades
printf '%s\n' 'Ubuntu bootstrap complete.' '다시 로그인한 뒤 /opt/cluemap 에서 docker compose를 실행하세요.' '실서버 인증서는 scripts/issue-certbot.sh, 백업은 scripts/backup-postgres.sh 로 진행하세요.'
