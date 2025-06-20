import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User
import os # 新增导入 os

class RegisterWindow:
    def __init__(self, master, users, on_register_success):
        self.master = master
        self.top = tk.Toplevel(master)
        self.top.title("用户注册")
        self.users = users
        self.on_register_success = on_register_success

        # 设置窗口大小和位置
        window_width = 450 # 稍微加宽窗口以容纳按钮
        window_height = 450 # 稍微加高窗口
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.top.resizable(False, False) # 禁止调整窗口大小

        self.book_categories = self.load_book_categories() # 加载书籍类别
        self.create_widgets()

    def load_book_categories(self):
        """从 books.txt 加载并返回唯一的书籍类别列表"""
        categories = set()
        try:
            # 获取当前脚本所在的目录，然后构建 books.txt 的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            books_file_path = os.path.join(current_dir, '..', 'data', 'books.txt')
            
            with open(books_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        parts = line.strip().split('|')
                        if len(parts) > 3:
                            category = parts[3].strip()
                            if category:
                                categories.add(category)
        except FileNotFoundError:
            messagebox.showerror("错误", f"无法找到书籍数据文件: {books_file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"加载书籍类别失败: {str(e)}")
        return sorted(list(categories))

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.top, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 用户名输入
        ttk.Label(main_frame, text="用户名:").grid(row=0, column=0, sticky=tk.W)
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # 密码输入
        ttk.Label(main_frame, text="密码:").grid(row=1, column=0, sticky=tk.W)
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # 偏好类别输入
        ttk.Label(main_frame, text="偏好类别(逗号分隔):").grid(row=2, column=0, sticky=tk.W)
        self.preferences_entry = ttk.Entry(main_frame)
        self.preferences_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # 类别按钮框架
        categories_container = ttk.Frame(main_frame)
        categories_container.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

        # 创建Canvas和滚动条
        canvas = tk.Canvas(categories_container)
        scrollbar = ttk.Scrollbar(categories_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # 配置Canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # 布局组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 创建标签框架
        categories_frame = ttk.LabelFrame(scrollable_frame, text="选择偏好类别", padding="10")
        categories_frame.pack(fill="both", expand=True)

        # 创建类别按钮
        row_num = 0
        col_num = 0
        max_cols = 4
        button_width = 15
        if self.book_categories:
            for category in self.book_categories:
                button = ttk.Button(categories_frame, text=category, width=button_width,
                                    command=lambda c=category: self.add_preference(c))
                button.grid(row=row_num, column=col_num, padx=5, pady=2, sticky=tk.W)
                col_num += 1
                if col_num >= max_cols:
                    col_num = 0
                    row_num += 1

        # 注册按钮
        ttk.Button(main_frame, text="注册", command=self.register).grid(row=4, column=0, columnspan=2, pady=20) # 行号调整为4

        # 设置容器权重
        categories_container.rowconfigure(0, weight=1)
        categories_container.columnconfigure(0, weight=1)

    def add_preference(self, category_to_add):
        """将选择的类别添加到偏好输入框"""
        current_preferences = self.preferences_entry.get().strip()
        if current_preferences:
            # 检查是否已存在该类别
            pref_list = [p.strip() for p in current_preferences.split(',')]
            if category_to_add not in pref_list:
                self.preferences_entry.insert(tk.END, f",{category_to_add}")
            else:
                messagebox.showinfo("提示", f"类别 '{category_to_add}' 已在您的偏好中。")
        else:
            self.preferences_entry.insert(tk.END, category_to_add)

    def register(self):
        # 直接从输入框获取值并去空格
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        preferences = self.preferences_entry.get().strip().split(',') if self.preferences_entry.get().strip() else []

        # 输入验证
        if not username:
            messagebox.showwarning("警告", "请输入用户名！")
            self.username_entry.focus()
            return
        if not password:
            messagebox.showwarning("警告", "请输入密码！")
            self.password_entry.focus()
            return

        # 检查用户名重复
        if any(u.username == username for u in self.users):
            messagebox.showerror("错误", "用户名已存在！")
            self.clear_entries()
            self.username_entry.focus()
            return

        # 生成用户ID
        new_user_id = max([u.user_id for u in self.users] + [0]) + 1
        new_user = User(new_user_id, username, password, preferences)
        self.users.append(new_user)
        self.save_user_to_file(new_user)

        self.on_register_success(new_user)
        self.top.destroy()

    def save_user_to_file(self, user):
        """按指定格式写入文件，确保空字段用空字符串占位"""
        preferences_str = ",".join(user.preferences) if user.preferences else ""
        read_books_str = ",".join(map(str, user.read_books)) if user.read_books else ""
        ratings_str = ",".join([f"{bid}:{rating:.1f}" for bid, rating in user.ratings.items()]) if user.ratings else ""
        
        # 构建 users.txt 的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        users_file_path = os.path.join(current_dir, '..', 'data', 'users.txt')

        user_line = f"{user.user_id}|{user.username}|{user.password}|{preferences_str}|{read_books_str}|{ratings_str}"

        try:
            # 检查文件末尾是否已有换行符
            needs_newline = True
            if os.path.exists(users_file_path) and os.path.getsize(users_file_path) > 0:
                with open(users_file_path, 'rb+') as f: # 以二进制读写模式打开
                    f.seek(-1, os.SEEK_END) # 移动到文件末尾的前一个字节
                    if f.read(1) == b'\n':
                        needs_newline = False
            
            with open(users_file_path, "a", encoding="utf-8") as f:
                if needs_newline and os.path.getsize(users_file_path) > 0: # 如果文件非空且需要换行
                    f.write("\n")
                f.write(user_line)
                f.write("\n") # 确保每个用户条目后都有换行符
        except Exception as e:
            messagebox.showerror("错误", f"保存用户失败：{str(e)}")

    def clear_entries(self):
        """清空所有输入框内容"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.preferences_entry.delete(0, tk.END)
