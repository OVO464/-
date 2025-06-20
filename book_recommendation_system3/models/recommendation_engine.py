import random
from collections import defaultdict
from .collaborative_filtering import UserBasedCollaborativeFiltering 
from .content_based import ContentBasedRecommender 
from .user import User  
from .book import Book  
import os # <--- 确保 os 也被导入，因为 load_ratings_from_file 中用到了

class RecommendationEngine:
    def __init__(self, books=None, users=None):
        self.books = books if books else []
        self.users = users if users else []
        self.user_by_username = {} # 方便通过用户名查找用户
        self.book_by_id = {}
        self.books_by_category = defaultdict(list)

        if books:
            self._index_books()
        if users: # 索引用户
            self._index_users()

        # 初始化新的推荐器
        if books and users:
            self.cf_recommender = UserBasedCollaborativeFiltering(users, books)
            self.content_recommender = ContentBasedRecommender(books)
            self.load_ratings_from_file() # 加载历史评分
        else:
            self.cf_recommender = None
            self.content_recommender = None

    def _index_books(self):
        """为图书建立索引，便于快速查找"""
        self.book_by_id = {book.book_id: book for book in self.books}
        self.books_by_category = defaultdict(list)
        for book in self.books:
            self.books_by_category[book.category].append(book)
    
    def _index_users(self): # 新增方法
        """为用户建立索引，便于快速查找"""
        self.user_by_username = {user.username: user for user in self.users}

    def add_book(self, book):
        """添加新书到系统"""
        self.books.append(book)
        self.book_by_id[book.book_id] = book
        self.books_by_category[book.category].append(book)
    
    def add_user(self, user):
        """添加新用户到系统"""
        if user.username not in self.user_by_username: # 避免重复添加
            self.users.append(user)
            self.user_by_username[user.username] = user

    def add_rating(self, user_obj, book_obj, rating):
        """添加用户对图书的评分，并更新相关信息"""
        if not isinstance(user_obj, User) or not isinstance(book_obj, Book):
            print("Error: Invalid user or book object provided for rating.")
            return

        # 更新User对象的评分记录
        # 假设User类有add_rating(book_id, rating)方法
        user_obj.add_rating(book_obj.book_id, float(rating))

        # 更新Book对象的评分信息
        # 假设Book类有add_rating(rating)方法来更新平均分和评分数
        book_obj.add_rating(float(rating))

        # 更新协同过滤推荐器中的数据（如果存在）
        if self.cf_recommender:
            # UserBasedCollaborativeFiltering可能需要一个方法来更新特定用户的评分
            # 或者在获取推荐时动态地从User对象获取最新评分
            # 一个简单的做法是标记需要重新构建或更新内部数据结构
            self.cf_recommender.update_user_rating(user_obj, book_obj.book_id, float(rating))
            # 或者更简单粗暴但可能低效：self.retrain_models() 
            # 但频繁retrain可能开销大，具体取决于cf_recommender的实现

        print(f"Rating added: User '{user_obj.username}' rated '{book_obj.title}' with {rating}")
        # 考虑是否需要在这里重新训练模型，或者标记模型为stale
        # self.retrain_models() # 每次评分都重新训练可能效率不高，看情况决定

    def load_ratings_from_file(self, file_path="data/user_ratings.txt"):
        """从文件加载历史评分数据并更新到系统中"""
        try:
            # 修正文件路径的查找方式，使其相对于项目根目录或models目录
            # 这里假设data文件夹与models文件夹在同一父目录下，即项目根目录下的data/
            current_dir = os.path.dirname(__file__) # models目录
            project_root = os.path.dirname(current_dir) # 项目根目录
            actual_file_path = os.path.join(project_root, file_path)

            if not os.path.exists(actual_file_path):
                print(f"Ratings file not found at {actual_file_path}. No ratings loaded.")
                return

            with open(actual_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        username, book_title, rating_str = parts
                        rating = float(rating_str)
                        
                        user = self.user_by_username.get(username)
                        # 需要一种方式通过title找到book_id或book_obj
                        # 假设book_by_id已经通过book.title索引，或者有一个book_by_title的索引
                        # 为了简单，我们先假设能通过title找到book对象
                        # 更好的做法是user_ratings.txt中存储book_id
                        book = next((b for b in self.books if b.title == book_title), None)

                        if user and book:
                            # 调用已有的add_rating逻辑，但避免重复写入文件和打印信息
                            # 这里我们直接更新对象，因为是从文件加载
                            user.add_rating(book.book_id, rating) # 假设User类有此方法
                            book.add_rating(rating)      # 假设Book类有此方法
                            print(f"Loaded rating from file: {username}, {book_title}, {rating}")
                        else:
                            if not user:
                                print(f"Warning: User '{username}' not found while loading ratings.")
                            if not book:
                                print(f"Warning: Book '{book_title}' not found while loading ratings.")
            
            # 加载完所有评分后，可能需要更新或重新训练推荐模型
            if self.cf_recommender:
                 # 理想情况下，cf_recommender应该能批量更新或基于当前用户和书籍对象重建
                self.cf_recommender.build_similarity_matrix() # 假设有这样的方法
            print("All ratings loaded from file and models updated.")

        except Exception as e:
            print(f"Error loading ratings from file: {e}")

    def get_book_by_id(self, book_id):
        """通过ID获取图书"""
        return self.book_by_id.get(book_id)
    
    def get_books_by_category(self, category):
        """获取特定类别的所有图书"""
        return self.books_by_category.get(category, [])
    
    def get_all_categories(self):
        """获取所有可用的图书类别"""
        return list(self.books_by_category.keys())
    
    def get_top_rated_books(self, n=10):
        """获取评分最高的n本书"""
        sorted_books = sorted(self.books, key=lambda x: (x.rating, x.ratings_count), reverse=True)
        return sorted_books[:n]
    
    def get_recommendations_for_user(self, user, n=10):
        """混合推荐：结合多种策略"""
        recommended_ids = set()
        result = []

        # 优先策略：协同过滤 (如果可用且用户有足够评分)
        if self.cf_recommender and len(user.ratings) > 2: # 假设用户至少有3个评分才用CF
            cf_recs = self.cf_recommender.recommend(user, n=n*2) # 获取多一些候选
            for book in cf_recs:
                if book.book_id not in user.ratings and book.book_id not in recommended_ids:
                    result.append(book)
                    recommended_ids.add(book.book_id)
                if len(result) >= n:
                    return result[:n]
        
        # 第二策略：基于内容的推荐 (如果可用)
        if self.content_recommender:
            content_recs = self.content_recommender.recommend(user, n=n*2)
            for book in content_recs:
                if book.book_id not in user.ratings and book.book_id not in recommended_ids:
                    result.append(book)
                    recommended_ids.add(book.book_id)
                if len(result) >= n:
                    return result[:n]

        # 第三策略：基于用户偏好类别 (如原有逻辑)
        preferred_categories = user.preferences
        if preferred_categories:
            candidate_books = []
            for category in preferred_categories:
                candidate_books.extend(self.books_by_category.get(category, []))
            
            # 按评分和评分数排序 (可以加入NLP相似度作为次要排序依据)
            candidate_books = sorted(candidate_books, key=lambda x: (x.rating, x.ratings_count), reverse=True)
            for book in candidate_books:
                if book.book_id not in user.ratings and book.book_id not in recommended_ids:
                    result.append(book)
                    recommended_ids.add(book.book_id)
                if len(result) >= n:
                    return result[:n]
        
        # 第四策略：高评分补充 (如原有逻辑)
        top_rated = self.get_top_rated_books(n=n*3) # 获取更多候选
        for book in top_rated:
            if book.book_id not in user.ratings and book.book_id not in recommended_ids:
                result.append(book)
                recommended_ids.add(book.book_id)
            if len(result) >= n:
                return result[:n]
        
        # 最后策略：随机补充 (如原有逻辑)
        if len(result) < n:
            available_books = [book for book in self.books if book.book_id not in user.ratings and book.book_id not in recommended_ids]
            if available_books:
                random.shuffle(available_books)
                for book in available_books:
                    result.append(book)
                    recommended_ids.add(book.book_id)
                    if len(result) >= n:
                        break
                        
        return result[:n]

    # 你可能还需要一个方法来重新训练/更新推荐模型，例如当有新用户、新书或新评分时
    def retrain_models(self):
        if self.books and self.users:
            print("Retraining recommendation models...")
            self.cf_recommender = UserBasedCollaborativeFiltering(self.users, self.books)
            self.content_recommender = ContentBasedRecommender(self.books)
            print("Models retrained.")
        else:
            print("Not enough data to retrain models.")