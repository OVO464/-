import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User
from gui.register_window import RegisterWindow
import os # 新增导入 os 模块

class LoginWindow:
    def __init__(self, master, users, on_login_success):
        self.master = master
        self.master.withdraw()  # 先隐藏主窗口

        self.top = tk.Toplevel(master) # 修改为 Toplevel
        self.top.title("图书推荐系统 - 用户登录") # 修改窗口标题
        self.users = users
        self.on_login_success = on_login_success

        # 设置窗口大小和位置
        window_width = 350 # 调整窗口宽度
        window_height = 300 # 调整窗口高度
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.top.resizable(False, False) # 禁止调整窗口大小

        self.create_widgets()

        # 添加窗口关闭事件处理
        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.top.grab_set() # 设置为模态对话框

    def on_closing(self):
        """处理窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？", parent=self.top):
            self.top.destroy()
            self.master.destroy()  # 确保主程序也被关闭

    def create_widgets(self):
        # 背景色等可以根据喜好调整
        # self.top.configure(bg="#f0f0f0") 

        # 添加一个Logo图片 (保证logo图片在 gui 目录下)
        try:
            base_path = os.path.dirname(__file__) # 获取当前文件所在目录
            logo_path = os.path.join(base_path, "smart.png") # logo图片名为smart.png
            self.logo_image = tk.PhotoImage(file=logo_path)
            logo_label = ttk.Label(self.top, image=self.logo_image)
            logo_label.place(x=145, y=20) # 根据图片大小调整位置
        except tk.TclError:
            print("Logo image not found or other Error")
            
        # 用户名输入
        ttk.Label(self.top, text="用户名:").place(x=50, y=100) # 使用 place 布局
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.top, textvariable=self.username_var, width=25)
        self.username_entry.place(x=120, y=100)

        # 密码输入
        ttk.Label(self.top, text="密  码:").place(x=50, y=140) # 使用 place 布局
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.top, textvariable=self.password_var, show="*", width=25)
        self.password_entry.place(x=120, y=140)

        # 按钮
        login_button = ttk.Button(self.top, text="登录", command=self.login, width=10)
        login_button.place(x=70, y=200)

        recover_button = ttk.Button(self.top, text="找回密码", command=self.show_recover_password, width=10)
        recover_button.place(x=180, y=200)

        register_button = ttk.Button(self.top, text="注册", command=self.show_register_window, width=22)
        register_button.place(x=70, y=240)
        
        self.username_entry.focus_set() # 设置初始焦点

    def login(self):
        # 直接从输入框获取值
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # 打印调试信息，确认获取到的值
        print(f"用户名输入: {username}")
        print(f"密码输入: {'*' * len(password)}")

        # 分别判断用户名和密码是否为空
        if not username:
            messagebox.showwarning("警告", "请输入用户名！")
            self.username_entry.focus()
            return

        if not password:
            messagebox.showwarning("警告", "请输入密码！")
            self.password_entry.focus()
            return

        # 先检查用户名是否存在
        user_exists = any(u.username == username for u in self.users)
        if not user_exists:
            messagebox.showerror("错误", "用户名不存在！")
            self.username_var.set("")  # 清空用户名
            self.password_var.set("")  # 清空密码
            self.username_entry.focus()  # 焦点设置到用户名框
            return

        # 检查密码是否正确
        user = next((u for u in self.users if u.username == username and u.password == password), None)
        if user:
            self.on_login_success(user)  # 先调用登录成功的回调
            self.master.deiconify()  # 显示主窗口
            self.top.destroy()  # 销毁登录窗口
        else:
            messagebox.showerror("错误", "密码错误！")
            self.password_var.set("")  # 只清空密码
            self.password_entry.focus()  # 焦点设置到密码框

    def show_recover_password(self):
        """显示找回密码窗口"""
        recover_window = tk.Toplevel(self.top)
        recover_window.title("找回密码")

        # 设置窗口大小和位置
        window_width = 250
        window_height = 150
        screen_width = recover_window.winfo_screenwidth()
        screen_height = recover_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        recover_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 设置为模态窗口
        recover_window.transient(self.top)
        recover_window.grab_set()

        # 创建找回密码界面
        frame = ttk.Frame(recover_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="请输入用户名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        # 创建输入框
        self.recover_username_entry = ttk.Entry(frame)
        self.recover_username_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        def recover_password():
            # 直接从输入框获取用户名
            username = self.recover_username_entry.get().strip()
            if not username:
                messagebox.showwarning("警告", "请输入用户名！")
                return

            user = next((u for u in self.users if u.username == username), None)
            if user:
                messagebox.showinfo("找回密码", f"用户 {username} 的密码是: {user.password}")
                recover_window.destroy()
            else:
                messagebox.showerror("错误", "用户名不存在！")

        ttk.Button(frame, text="找回密码", command=recover_password).grid(row=2, column=0, pady=20)

        # 设置初始焦点
        self.recover_username_entry.focus()

    def show_register_window(self):
        RegisterWindow(self.top, self.users, self.on_register_success)

    def on_register_success(self, user):
        messagebox.showinfo("成功", f"注册成功，欢迎 {user.username}!")
