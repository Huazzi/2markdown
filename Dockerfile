FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads output

# 暴露端口
EXPOSE 5000

# 使用gunicorn运行应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"] 