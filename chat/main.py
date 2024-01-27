import grpc
import os
import time
import threading
import chat_pb2
import chat_pb2_grpc
import google.protobuf.timestamp_pb2

from ping3 import ping
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from google.protobuf.timestamp_pb2 import Timestamp


write_lock = threading.Lock()

class MessageReceiver(chat_pb2_grpc.ChatServiceServicer):
    def SendMessage(self, request, context):
        # print(f"Received message from {request.sender_name} ({request.sender_ip}): {request.text}")
        insert_mes(request)
        return chat_pb2.Empty()

def serve():
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(MessageReceiver(), server)
    server.add_insecure_port('[::]:50000')
    server.start()
    server.wait_for_termination()

def datetime_to_timestamp(dt):
    timestamp = Timestamp()
    timestamp.FromDatetime(dt)
    return timestamp

def insert_mes(msg):
    write_lock.acquire()
    try:
        with open(file_path, 'r+') as f:
            lines = f.readlines()
            temp = []
            # 假设 msg.timestamp 是一个 Timestamp 对象
            timestamp = msg.timestamp

            # 将 Timestamp 对象转换为 datetime 对象
            dt = datetime.fromtimestamp(timestamp.seconds + timestamp.nanos / 1e9)

            # 将 datetime 对象转换为字符串
            dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')

            while lines:
                last_line = lines[-1]
                last_timestamp = ' '.join(last_line.split()[:2])  # 获取整个日期和时间
                if last_timestamp < dt_str:
                    break
                else:
                    temp.append(lines.pop())
            lines.append(f"{dt_str} {msg.sender_name} ({msg.sender_ip}): {msg.text}\n")
            lines.extend(reversed(temp))
            f.seek(0)
            f.truncate()
            f.writelines(lines)
    finally:
        write_lock.release()

def show_mes_and_get_input():
    while True:
        # 清空终端
        os.system('cls' if os.name == 'nt' else 'clear')

        # 打开文件并打印其内容
        with open(file_path, 'r') as f:
            print(f.read())

        for peer in peer_ip:
            latency = ping(peer)
            if latency == None:
                print(f'Peer {peer} is offline')
            else:
                print(f'Peer {peer} is online, latency: {latency * 1000:.1f}ms')
        
        # 获取用户的输入, 如果输入为空, 则继续只是刷新终端更新内容
        message = input("Enter a message: ")
        if message != '' :return message

def run_client():
    while True:
        text = show_mes_and_get_input()
        now = datetime.now()
        for peer in peer_ip:
            channel = grpc.insecure_channel(f'{peer}:50000')
            stub = chat_pb2_grpc.ChatServiceStub(channel)
            message = chat_pb2.Message(
                text=text,
                timestamp=datetime_to_timestamp(now),
                sender_ip='localhost',
                sender_name=username,
                receiver_ip=peer,
                receiver_name='Server'
            )
            try:
                stub.SendMessage(message)
                # insert_mes(message)  # 只在消息发送成功后插入消息
            except Exception as e:
                print(f"Failed to send message to {peer}: {e}")


def generate_mes_file():
    # 初始化索引
    index = 1

    # 确保目录存在
    os.makedirs(dir_path, exist_ok=True)

    # 如果 mes.txt 文件存在
    if os.path.exists(file_path):
        # 如果 oldmes.txt 文件存在
        while os.path.exists(os.path.join(dir_path, f'oldmes{index}.txt')):
            # 更新索引
            index += 1

        # 重命名 mes.txt 文件
        os.rename(file_path, os.path.join(dir_path, f'oldmes{index}.txt'))

    # 创建新的 mes.txt 文件
    with open(file_path, 'w') as f:
        pass


if __name__ == '__main__':
    # 输入对方ip
    global username,peer_ip;
    peer_ip=['localhost']
    while True:
        peer_ip.append(input("Peer ip:"))
        if input("Any other peers?[y/n]:")!='y':
            break


    username=input("Your name:")
    dir_path = 'mes_set'
    file_path = os.path.join(dir_path, 'mes.txt')

    # 生成 mes.txt 文件
    generate_mes_file()

    # 启动服务器
    server_thread = threading.Thread(target=serve)
    server_thread.start()

    # 启动客户端
    client_thread = threading.Thread(target=run_client)
    client_thread.start()
    
    # 等待线程完成
    server_thread.join()
    client_thread.join()