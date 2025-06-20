class Book:
    def __init__(self, book_id, title, author, category, description, rating=0.0, ratings_count=0):
        self.book_id = str(book_id) # 确保book_id是字符串
        self.title = title
        self.author = author
        self.category = category
        self.description = description
        # 内部存储总评分和，以便精确计算平均分
        self._total_rating_sum = float(rating) * int(ratings_count)
        self.ratings_count = int(ratings_count)
        if self.ratings_count > 0:
            self.rating = round(self._total_rating_sum / self.ratings_count, 2)
        else:
            self.rating = 0.0

    def add_rating(self, new_rating):
        """为这本书添加一个新的评分，并更新平均分和评分总数"""
        try:
            new_rating = float(new_rating)
            if not (1 <= new_rating <= 5): # 假设评分范围是1-5
                print(f"Warning: Rating {new_rating} for book '{self.title}' is outside the valid range (1-5).")
                # 可以选择是否接受无效评分，或在此处抛出错误/忽略
                # return # 如果决定忽略无效评分

            self._total_rating_sum += new_rating
            self.ratings_count += 1
            if self.ratings_count > 0:
                self.rating = round(self._total_rating_sum / self.ratings_count, 2)
            # else 分支已在 __init__ 中处理，此处 ratings_count 必大于0
        except ValueError:
            print(f"Error: New rating '{new_rating}' is not a valid number for book '{self.title}'.")

    def __str__(self):
        return f"{self.title} by {self.author} (评分: {self.rating:.1f}/5.0, {self.ratings_count}人评价)"