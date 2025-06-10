FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 先安装依赖（利用 Docker 缓存）
COPY requirements.txt .

# 换源并安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 配置 pip 换源并安装 Python 依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    pip install --no-cache-dir Pillow && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . /app

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 启动命令
CMD ["python", "app.py"]
