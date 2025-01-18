import socket
import threading

# 定义服务器地址和端口
HOST = '127.0.0.1'
PORT = 12345

# 创建服务器套接字
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

clients = []
nicknames = []

# 从文件中加载用户信息
def load_users():
    users = {}
    try:
        with open('users.txt', 'r') as file:
            for line in file:
                username, password = line.strip().split(',')
                users[username] = password
    except FileNotFoundError:
        pass
    return users

# 将用户信息保存到文件中
def save_user(username, password):
    with open('users.txt', 'a') as file:
        file.write(f'{username},{password}\n')

users = load_users()

# 广播消息给所有客户端
def broadcast(message):
    for client in clients:
        client.send(message)

# 处理客户端连接
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} 离开了聊天室!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# 接受客户端连接
def receive():
    while True:
        client, address = server.accept()
        print(f'连接来自 {str(address)}')

        client.send('LOGIN_OR_REGISTER'.encode('utf-8'))
        action = client.recv(1024).decode('utf-8')

        if action == 'REGISTER':
            client.send('REGISTER'.encode('utf-8'))
            credentials = client.recv(1024).decode('utf-8')
            username, password = credentials.split(',')
            if username in users:
                client.send('USER_EXISTS'.encode('utf-8'))
                client.close()
            else:
                users[username] = password
                save_user(username, password)
                client.send('REGISTER_SUCCESS'.encode('utf-8'))
                client.close()
        elif action == 'LOGIN':
            client.send('LOGIN'.encode('utf-8'))
            credentials = client.recv(1024).decode('utf-8')
            username, password = credentials.split(',')

            if username in users and users[username] == password:
                client.send('LOGIN_SUCCESS'.encode('utf-8'))
                nicknames.append(username)
                clients.append(client)

                print(f'昵称是 {username}!')
                broadcast(f'{username} 加入了聊天室!'.encode('utf-8'))
                client.send('连接到服务器!'.encode('utf-8'))

                thread = threading.Thread(target=handle_client, args=(client,))
                thread.start()
            else:
                client.send('LOGIN_FAIL'.encode('utf-8'))
                client.close()

print('服务器正在运行...')
receive()
