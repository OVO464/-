from models.book import Book
from models.user import User

def load_books():
    """从books.txt加载图书数据"""
    books = []
    try:
        with open('data/books.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                book_id, title, author, category, description, rating, ratings_count = line.strip().split('|')
                books.append(Book(
                    int(book_id),
                    title,
                    author,
                    category,
                    description,
                    float(rating),
                    int(ratings_count)
                ))
    except FileNotFoundError:
        print("警告：books.txt文件不存在")
    return books

def load_users():
    """从users.txt加载用户数据"""
    users = []
    try:
        with open('data/users.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                print(f"正在处理用户数据行: {line.strip()}")  # 添加调试信息
                user_id, username, password, preferences, read_books, ratings = line.strip().split('|')
                
                # 处理偏好类别
                preferences = preferences.split(',') if preferences else []
                
                # 创建用户对象
                user = User(int(user_id), username, password, preferences)
                print(f"成功创建用户对象: {user.username}")  # 添加调试信息
                
                # 添加已读书籍
                if read_books:
                    user.read_books = [int(book_id) for book_id in read_books.split(',')]
                
                # 添加评分记录
                if ratings:
                    for rating in ratings.split(','):
                        book_id, score = rating.split(':')
                        user.add_rating(int(book_id), float(score))
                        
                users.append(user)
                
        print(f"总共加载了 {len(users)} 个用户")  # 添加调试信息
    except FileNotFoundError:
        print("警告：users.txt文件不存在，请检查文件路径")
    except Exception as e:
        print(f"加载用户数据时发生错误: {str(e)}")
    return users

def load_sample_data():
    """加载所有数据"""
    books = load_books()
    users = load_users()
    return books, users