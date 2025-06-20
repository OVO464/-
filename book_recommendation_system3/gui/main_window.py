import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import threading # <--- 添加 threading 导入
from models.recommendation_engine import RecommendationEngine
from models.user import User
from models.book import Book
from data.sample_data import load_sample_data
from gui.login_window import LoginWindow
from openai import OpenAI # <--- 添加 OpenAI 导入

class MainWindow:
    def __init__(self, master, books, users): # 添加 books 和 users 参数
        self.master = master
        # 设置主窗口标题和大小
        self.master.title("图书推荐系统 - O.o")
        window_width = 550 # 调整窗口宽度
        window_height = 400 # 调整窗口高度
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing) # 添加关闭事件处理

        self.engine = RecommendationEngine()
        self.books = books 
        self.users = users 
        self.setup_data() 
        self.current_user = None
        self.ai_thread = None # 用于跟踪AI线程
        self.stop_ai_event = threading.Event() # 用于停止AI线程的事件
        self.show_login_window()
        
    def setup_data(self):
        # 加载示例数据
        # self.books, self.users = load_sample_data() # 不再需要重新加载
        for book in self.books:
            self.engine.add_book(book)
        for user in self.users:
            self.engine.add_user(user)
    
    def show_login_window(self):
        """显示登录窗口"""
        LoginWindow(self.master, self.users, self.on_login_success)
    
    def on_login_success(self, user):
        """登录成功回调"""
        self.current_user = user
        # 登录成功后显示主窗口
        self.master.deiconify()
        self.create_widgets()
        messagebox.showinfo("成功", f"欢迎, {user.username}!")
    
    def create_widgets(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加标签页控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建"首页"标签页 
        self.image_display_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.image_display_frame, text="首页")

        # 加载并显示图片
        try:
            base_path = os.path.dirname(__file__) # 获取当前文件所在目录
            image_path = os.path.join(base_path, "very_good.png") # image图片名为very_good.png
            if os.path.exists(image_path):
                pil_image = Image.open(image_path)
                self.img = ImageTk.PhotoImage(pil_image)
                image_label = ttk.Label(self.image_display_frame, image=self.img)
                image_label.pack(expand=True)
            else:
                ttk.Label(self.image_display_frame, text="图片文件未找到!").pack(expand=True)
        except Exception as e:
            print(f"加载图片时出错: {e}")
            ttk.Label(self.image_display_frame, text=f"加载图片失败: {e}").pack(expand=True)
        
        # 创建"所有图书"标签页
        self.all_books_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.all_books_frame, text="所有图书")
        # 配置all_books_frame的行列权重使其内部控件可以缩放
        self.all_books_frame.grid_rowconfigure(0, weight=1)
        self.all_books_frame.grid_columnconfigure(0, weight=1)
        
        # 创建图书列表
        self.books_text = tk.Text(self.all_books_frame, height=15, width=60)
        self.books_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S)) 
        books_scrollbar = ttk.Scrollbar(self.all_books_frame, orient=tk.VERTICAL, command=self.books_text.yview)
        books_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.books_text['yscrollcommand'] = books_scrollbar.set
        
        # 显示所有图书
        self.display_all_books()
        
        # 创建"推荐系统"标签页
        self.recommend_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recommend_frame, text="图书推荐")
        # 配置recommend_frame的行列权重使其内部控件可以缩放
        self.recommend_frame.grid_rowconfigure(2, weight=1) # 让文本框所在行可以扩展
        self.recommend_frame.grid_columnconfigure(0, weight=1) # 让文本框所在列可以扩展 (跨列了，所以配置第0列)
        self.recommend_frame.grid_columnconfigure(1, weight=1) 
        self.recommend_frame.grid_columnconfigure(2, weight=1)
        
        # 显示当前用户
        ttk.Label(self.recommend_frame, text="当前用户:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(self.recommend_frame, text=self.current_user.username).grid(row=0, column=1, sticky=tk.W)  
        
        # 新增：显示用户偏好
        ttk.Label(self.recommend_frame, text="偏好:").grid(row=1, column=0, sticky=tk.W, pady=(5,0))
        preferences = getattr(self.current_user, 'preferences', [])  # 获取用户偏好，无则空列表
        preferences_text = ", ".join(preferences) if preferences else "未设置偏好"
        ttk.Label(self.recommend_frame, text=preferences_text).grid(row=1, column=1, sticky=tk.W, pady=(5,0))  # 新增行
        
        # 推荐按钮
        ttk.Button(self.recommend_frame, text="获取推荐", command=self.show_recommendations).grid(row=0, column=2, padx=5)
        
        # 推荐结果显示区域
        #ttk.Label(self.recommend_frame, text="推荐图书:").grid(row=2, column=0, sticky=tk.W, pady=(10,0))
        self.result_text = tk.Text(self.recommend_frame, height=10, width=50)
        self.result_text.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S)) # 修改sticky
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.recommend_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        self.result_text['yscrollcommand'] = scrollbar.set

        # 创建"图书评分"标签页
        self.rating_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rating_frame, text="图书评分")
        self.create_rating_widgets()

        # 创建"AI对话"标签页
        self.ai_chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_chat_frame, text="AI 对话")
        self.create_ai_chat_widgets()

        # 让主窗口的行列权重配置正确，使得notebook能够随窗口缩放
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    def display_all_books(self):
        """显示所有图书"""
        self.books_text.delete(1.0, tk.END)
        for book in self.books:
            self.books_text.insert(tk.END, f"书名: {book.title}\n")
            self.books_text.insert(tk.END, f"作者: {book.author}\n")
            self.books_text.insert(tk.END, f"类别: {book.category}\n")
            self.books_text.insert(tk.END, f"评分: {book.rating}\n")
            self.books_text.insert(tk.END, f"简介: {book.description}\n")
            self.books_text.insert(tk.END, "-" * 50 + "\n")
    
    def show_recommendations(self):
        """显示推荐结果"""
        if self.current_user:
            recommendations = self.engine.get_recommendations_for_user(self.current_user)
            self.result_text.delete(1.0, tk.END)
            for i, book in enumerate(recommendations, 1):
                self.result_text.insert(tk.END, f"{i}. {book.title} (作者: {book.author})\n")
        else:
            messagebox.showerror("错误", "请先登录！")

    def on_closing(self):
        """处理主窗口关闭事件"""
        if self.ai_thread and self.ai_thread.is_alive():
            self.stop_ai_event.set() # 尝试停止AI线程
            self.ai_thread.join(timeout=1) # 等待线程一小段时间
        if messagebox.askokcancel("退出", "确定要退出程序吗?"):
            self.master.quit()
            self.master.destroy()

    def create_rating_widgets(self):
        """创建图书评分标签页的控件"""
        self.rating_frame.grid_columnconfigure(1, weight=1) # 让控件列可以扩展

        ttk.Label(self.rating_frame, text="选择图书:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.book_to_rate_var = tk.StringVar()
        book_titles = [book.title for book in self.books]
        self.book_rating_combobox = ttk.Combobox(self.rating_frame, textvariable=self.book_to_rate_var, values=book_titles, state="readonly", width=40)
        self.book_rating_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        if book_titles:
            self.book_rating_combobox.current(0)

        ttk.Label(self.rating_frame, text="选择评分:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.rating_var = tk.IntVar(value=3) # 默认3星
        rating_scale = ttk.Scale(self.rating_frame, from_=1, to=5, orient=tk.HORIZONTAL, variable=self.rating_var, command=lambda s: self.rating_var.set(int(float(s))))
        rating_scale.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        # 显示当前评分值
        self.current_rating_label = ttk.Label(self.rating_frame, text=f"当前评分: {self.rating_var.get()}")
        self.current_rating_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.rating_var.trace_add("write", lambda *args: self.current_rating_label.config(text=f"当前评分: {self.rating_var.get()}"))


        submit_rating_button = ttk.Button(self.rating_frame, text="提交评分", command=self.submit_rating)
        submit_rating_button.grid(row=2, column=1, padx=5, pady=10, sticky=tk.E)

    def submit_rating(self):
        """提交用户对图书的评分"""
        if not self.current_user:
            messagebox.showerror("错误", "请先登录后再评分！")
            return

        book_title = self.book_to_rate_var.get()
        rating = self.rating_var.get()

        if not book_title:
            messagebox.showwarning("提示", "请选择一本图书进行评分！")
            return
        
        # 确认评分
        confirm = messagebox.askyesno("确认评分", f"您确定要为《{book_title}》评分为 {rating} 星吗？")
        if not confirm:
            return

        try:
            # 获取data文件夹的路径，确保与books.txt, users.txt在同一目录下
            base_data_path = os.path.join(os.path.dirname(__file__), '..', 'data')
            if not os.path.exists(base_data_path):
                os.makedirs(base_data_path) # 如果data目录不存在则创建
            
            ratings_file_path = os.path.join(base_data_path, "user_ratings.txt")
            
            # 检查是否已对该书评过分，如果评过则更新，否则追加
            updated = False
            lines = []
            if os.path.exists(ratings_file_path):
                with open(ratings_file_path, 'r', encoding='utf-8') as f_read:
                    for line in f_read:
                        parts = line.strip().split(',')
                        if len(parts) == 3 and parts[0] == self.current_user.username and parts[1] == book_title:
                            lines.append(f"{self.current_user.username},{book_title},{rating}\n")
                            updated = True
                        else:
                            lines.append(line)
            
            if not updated:
                lines.append(f"{self.current_user.username},{book_title},{rating}\n")

            with open(ratings_file_path, 'w', encoding='utf-8') as f_write:
                f_write.writelines(lines)

            messagebox.showinfo("成功", f"《{book_title}》评分 {rating} 已保存！")
            
            # 更新 RecommendationEngine 中的用户评分数据（如果需要实时更新推荐）
            # 首先找到对应的Book对象
            selected_book = next((book for book in self.books if book.title == book_title), None)
            if selected_book:
                # 假设User对象有一个方法可以更新或添加评分
                # self.current_user.add_rating(selected_book.book_id, rating) # 需要User类支持
                # 或者直接更新引擎中的用户对书的评分记录
                self.engine.add_rating(self.current_user, selected_book, rating)
                print(f"Debug: Rating added to engine for user {self.current_user.username}, book {selected_book.title}, rating {rating}")

        except Exception as e:
            messagebox.showerror("错误", f"保存评分失败: {e}")
            print(f"保存评分时出错: {e}")

    def display_all_books(self):
        """显示所有图书"""
        self.books_text.delete(1.0, tk.END)
        for book in self.books:
            self.books_text.insert(tk.END, f"书名: {book.title}\n")
            self.books_text.insert(tk.END, f"作者: {book.author}\n")
            self.books_text.insert(tk.END, f"类别: {book.category}\n")
            self.books_text.insert(tk.END, f"评分: {book.rating}\n")
            self.books_text.insert(tk.END, f"简介: {book.description}\n")
            self.books_text.insert(tk.END, "-" * 50 + "\n")

    def create_ai_chat_widgets(self):
        """创建AI对话标签页的控件"""
        self.ai_chat_frame.grid_rowconfigure(0, weight=1) # 让对话历史文本框可以扩展
        self.ai_chat_frame.grid_columnconfigure(0, weight=1) # 让控件列可以扩展

        # 对话历史显示区域
        self.chat_history_text = tk.Text(self.ai_chat_frame, height=15, width=60, state=tk.DISABLED) # 初始时不可编辑
        self.chat_history_text.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5) # columnspan 调整为3
        chat_scrollbar = ttk.Scrollbar(self.ai_chat_frame, orient=tk.VERTICAL, command=self.chat_history_text.yview)
        chat_scrollbar.grid(row=0, column=3, sticky=(tk.N, tk.S), pady=5) # scrollbar 放到第4列
        self.chat_history_text['yscrollcommand'] = chat_scrollbar.set

        # 用户输入框
        self.user_input_entry = ttk.Entry(self.ai_chat_frame, width=50)
        self.user_input_entry.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.user_input_entry.bind("<Return>", self.send_to_deepseek) # 绑定回车键

        # 发送按钮
        self.send_button = ttk.Button(self.ai_chat_frame, text="发送", command=self.send_to_deepseek)
        self.send_button.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)

        # 停止按钮
        self.stop_ai_button = ttk.Button(self.ai_chat_frame, text="停止", command=self.stop_ai_response, state=tk.DISABLED)
        self.stop_ai_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)

    def stop_ai_response(self):
        """停止当前的AI响应"""
        if self.ai_thread and self.ai_thread.is_alive():
            self.stop_ai_event.set() # 设置事件，通知线程停止
            self.chat_history_text.config(state=tk.NORMAL)
            self.chat_history_text.insert(tk.END, "\n[AI响应已停止]\n")
            self.chat_history_text.config(state=tk.DISABLED)
            self.chat_history_text.see(tk.END)
        self.send_button.config(state=tk.NORMAL)
        self.stop_ai_button.config(state=tk.DISABLED)

    def send_to_deepseek(self, event=None): # event 参数用于处理回车键绑定
        user_message = self.user_input_entry.get()
        if not user_message.strip():
            messagebox.showwarning("提示", "请输入您想发送的内容！")
            return

        if self.ai_thread and self.ai_thread.is_alive():
            messagebox.showwarning("提示", "AI正在回复中，请稍候或点击停止后再发送新消息。")
            return

        # 在对话历史中显示用户消息
        self.chat_history_text.config(state=tk.NORMAL)
        self.chat_history_text.insert(tk.END, f"您: {user_message}\n")
        self.chat_history_text.config(state=tk.DISABLED)
        self.chat_history_text.see(tk.END) # 滚动到底部
        self.user_input_entry.delete(0, tk.END) # 清空输入框

        # 显示AI正在回复的初始提示
        self.chat_history_text.config(state=tk.NORMAL)
        self.chat_history_text.insert(tk.END, "AI: ") # AI回复前缀
        self.chat_history_text.config(state=tk.DISABLED)
        self.chat_history_text.see(tk.END)
        self.master.update_idletasks() # 强制更新UI

        self.send_button.config(state=tk.DISABLED)
        self.stop_ai_button.config(state=tk.NORMAL)
        self.stop_ai_event.clear() # 重置停止事件

        # 创建并启动新线程处理API调用
        self.ai_thread = threading.Thread(target=self._get_deepseek_response, args=(user_message,))
        self.ai_thread.daemon = True # 设置为守护线程，主程序退出时线程也退出
        self.ai_thread.start()

    def _get_deepseek_response(self, user_message):
        try:
            client = OpenAI(api_key="***", base_url="https://api.deepseek.com")//使用自己申请的api
            messages = [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_message},
            ]
            
            response_stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True
            )
            
            self.chat_history_text.config(state=tk.NORMAL)
            for chunk in response_stream:
                if self.stop_ai_event.is_set(): # 检查是否需要停止
                    break 
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    ai_content_part = chunk.choices[0].delta.content
                    self.chat_history_text.insert(tk.END, ai_content_part)
                    self.chat_history_text.see(tk.END) 
                    self.master.update_idletasks() 
            
            if not self.stop_ai_event.is_set():
                self.chat_history_text.insert(tk.END, "\n\n")
            self.chat_history_text.config(state=tk.DISABLED)
            self.chat_history_text.see(tk.END)

        except Exception as e:
            if not self.stop_ai_event.is_set(): # 只有在未被手动停止时才显示错误
                self.chat_history_text.config(state=tk.NORMAL)
                current_content = self.chat_history_text.get("1.0", tk.END)
                if current_content.endswith("AI: "):
                    self.chat_history_text.insert(tk.END, f"发生错误: {e}\n\n")
                else: 
                    self.chat_history_text.insert(tk.END, f"\nAI: 发生错误: {e}\n\n")
                self.chat_history_text.config(state=tk.DISABLED)
                self.chat_history_text.see(tk.END)
                # messagebox.showerror("API错误", f"与Deepseek API通信失败: {e}") # 不在线程中直接调用messagebox
                self.master.after(0, lambda: messagebox.showerror("API错误", f"与Deepseek API通信失败: {e}"))
        finally:
            # 确保按钮状态在线程结束时恢复
            self.master.after(0, self._finalize_ai_response)

    def _finalize_ai_response(self):
        """在AI响应完成后（成功、失败或停止）恢复按钮状态"""
        self.send_button.config(state=tk.NORMAL)
        self.stop_ai_button.config(state=tk.DISABLED)
        self.stop_ai_event.clear()

# 主程序入口 (如果直接运行此文件进行测试)
if __name__ == '__main__':
    root = tk.Tk()
    # MainWindow 初始化时会隐藏 root, LoginWindow 会创建 Toplevel
    # 为了直接测试 MainWindow，我们需要模拟登录成功
    class MockUser:
        def __init__(self, username):
            self.username = username

    app = MainWindow(root)
    # 模拟登录成功，以便显示主窗口内容进行测试
    # 正常流程中，这部分由 LoginWindow 的 on_login_success 回调触发
    # app.on_login_success(MockUser("testuser")) 
    # root.mainloop() # MainWindow的__init__中会调用show_login_window, LoginWindow会处理主循环
    # 因此，如果直接运行此文件，LoginWindow会先显示
    # 如果LoginWindow被关闭（例如通过其关闭按钮），程序会退出
    # 如果要直接测试MainWindow的UI，需要注释掉show_login_window的调用，并手动调用on_login_success
    root.mainloop()
