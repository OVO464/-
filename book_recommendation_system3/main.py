import tkinter as tk
from gui.main_window import MainWindow
from data.sample_data import load_sample_data

def main():
    # 获取图书和用户数据
    books, users = load_sample_data()

    root = tk.Tk()
    root.title("图书推荐系统")
    root.withdraw()  # 先隐藏主窗口
    app = MainWindow(root, books, users)  # 将books和users传递给MainWindow
    root.mainloop()

if __name__ == "__main__":
    main()
