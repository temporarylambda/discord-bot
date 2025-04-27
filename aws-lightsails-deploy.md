# AWS Lightsail Deployment Guide

1. 建立 Lightsail 實例 
    - 建議採用 4GB Ram 以避免記憶體不足導致 container 無法正常運作。
    - 請參考以下 Lightsail 啟動指令碼：
        ```bash
        #!/bin/bash

        # 更新系統
        sudo yum update -y

        # 安裝 Docker
        sudo yum install -y docker
        sudo systemctl start docker
        sudo systemctl enable docker

        # 安裝 Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose

        # 設定 ec2-user 使用 Docker 權限
        sudo usermod -aG docker ec2-user

        # 建立 2G Swap 空間
        sudo fallocate -l 2G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab

        # 安裝 git
        sudo yum install -y git
        ```
2. 完成 Github SSH 金鑰設定
    - `ssh-keygen -t ed25519 -C "temporary.lambda@gmail.com"`
    - `cat ~/.ssh/id_ed25519.pub`
    - 複製公鑰結果到 Github SSH 金鑰設定頁面並完成設定
    - `git clone git@github.com:temporarylambda/discord-bot.git`

3. 設定 .env 檔案
    - `cd discord-bot`
    - `cp .env.example .env`

4. 執行 Docker Compose
    - `docker-compose up -d`

5. 設定自動重啟 

```
# 建立 systemd 服務來開機自動啟動
sudo bash -c 'cat > /etc/systemd/system/discord-bot.service << EOF
[Unit]
Description=Discord Bot Docker Compose Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/home/ec2-user/discord-bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF'

# 重新載入 systemd
sudo systemctl daemon-reload

# 啟動並設定開機啟動
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
```