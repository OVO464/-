class User:
    def __init__(self, user_id, username, password, preferences=None, read_books=None, ratings=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.preferences = preferences if preferences is not None else []
        self.read_books = read_books if read_books is not None else [] # 初始化read_books
        self.ratings = ratings if ratings is not None else {} # 初始化ratings

    def add_preference(self, genre):
        if genre not in self.preferences:
            self.preferences.append(genre)

    def add_read_book(self, book_id): # 修改参数为 book_id
        if book_id not in self.read_books:
            self.read_books.append(book_id)

    def add_rating(self, book_id, rating):
        """添加用户对某本书的评分，并确保该书在已读列表中"""
        try:
            self.ratings[str(book_id)] = float(rating) # 确保book_id是字符串键，rating是浮点数
            # 如果对书评分了，也应该算作已读
            if str(book_id) not in self.read_books:
                self.read_books.append(str(book_id))
        except ValueError:
            print(f"Error: Rating '{rating}' is not a valid number for book_id '{book_id}'.")

    def get_rating(self, book_id):
        """获取用户对某本书的评分"""
        return self.ratings.get(book_id, None)

    def get_preferences(self):
        return self.preferences

    def get_read_books(self):
        return self.read_books