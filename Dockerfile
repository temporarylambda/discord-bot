# 使用 Python 3.10 作為基礎映像
FROM python:3.10

# 安裝 mysql-client 
RUN apt-get update && \ 
    apt-get install -y default-mysql-client && \ 
    rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /bot

# **先複製 requirements.txt**
COPY src/requirements.txt ./

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 執行指令
RUN alembic init alembic

# 設定環境變數 (避免 Python 產生緩存)
ENV PYTHONUNBUFFERED=1
