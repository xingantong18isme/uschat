import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

# 输入服务器地址和端口
HOST = '127.0.0.1'
PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("聊天室客户端")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.frame = tk.Frame(master)
        self.scrollbar = tk.Scrollbar(self.frame)
        self.msg_list = tk.Listbox(self.frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.msg_list.pack()
        self.frame.pack()

        self.entry_field = tk.Entry(master)
        self.entry_field.bind("<Return>", self.send)
        self.entry_field.pack()
        self.send_button = tk.Button(master, text="发送", command=self.send)
        self.send_button.pack()

        self.username = None
        self.login_or_register()

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def login_or_register(self):
        action = simpledialog.askstring("选择操作", "请选择操作 (登录: login, 注册: register):")
        if action == 'register':
            self.sock.send('REGISTER'.encode('utf-8'))
            self.register()
        elif action == 'login':
            self.sock.send('LOGIN'.encode('utf-8'))
            self.login()
        else:
            messagebox.showerror("错误", "无效的操作。")
            self.master.quit()

    def register(self):
        username = simpledialog.askstring("注册", "请输入用户名:")
        password = simpledialog.askstring("注册", "请输入密码:", show='*')
        self.sock.send(f'{username},{password}'.encode('utf-8'))
        response = self.sock.recv(1024).decode('utf-8')
        if response == 'USER_EXISTS':
            messagebox.showerror("错误", "用户名已存在，请重新注册。")
            self.master.quit()
        elif response == 'REGISTER_SUCCESS':
            messagebox.showinfo("成功", "注册成功，请重新登录。")
            self.master.quit()

    def login(self):
        username = simpledialog.askstring("登录", "请输入用户名:")
        password = simpledialog.askstring("登录", "请输入密码:", show='*')
        self.sock.send(f'{username},{password}'.encode('utf-8'))
        response = self.sock.recv(1024).decode('utf-8')
        if response == 'LOGIN_SUCCESS':
            self.username = username
            messagebox.showinfo("成功", "登录成功!")
        elif response == 'LOGIN_FAIL':
            messagebox.showerror("错误", "登录失败! 请检查用户名或密码。")
            self.master.quit()

    def receive(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                self.msg_list.insert(tk.END, message)
            except:
                messagebox.showerror("错误", "出现错误!")
                self.sock.close()
                break

    def send(self, event=None):
        message = self.entry_field.get()
        self.entry_field.set("")
        self.sock.send(f'{self.username}: {message}'.encode('utf-8'))

root = tk.Tk()
client = ChatClient(root)
root.mainloop()
