# 使用官方 Python 3.9 镜像作为基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 将宿主机上的文件复制到容器中的工作目录
COPY chat /app

# 更新apt-get并安装inetutils-ping,测试使用
#RUN apt-get update && apt-get install -y inetutils-ping

# 在容器中运行安装依赖
#RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
#使用HTTP,不安全但不会报SSL
RUN pip3 install --trusted-host pypi.tuna.tsinghua.edu.cn --index-url http://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 使用 CMD 指令来运行你的脚本
#CMD ["python", "/app/your_script.py"]
