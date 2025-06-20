from .nlp_utils import TextVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedRecommender:
    def __init__(self, books):
        self.books = books
        self.book_ids = [book.book_id for book in books]
        self.book_index_map = {book_id: i for i, book_id in enumerate(self.book_ids)}
        self.similarity_matrix = self._calculate_similarity_matrix()

    def _calculate_similarity_matrix(self):
        """计算书籍之间的内容相似度矩阵"""
        # 假设每本书籍对象有一个 'get_content_features_text' 方法，返回用于比较的文本
        # 例如，可以是 "标题 类别 简介 标签 作者"
        # 或者直接使用 book.description
        documents = [book.description if book.description else "" for book in self.books] 
        
        if not any(documents): # 如果所有描述都为空
            # 返回一个单位矩阵或零矩阵，表示没有内容相似性信息
            num_books = len(self.books)
            return [[(1.0 if i == j else 0.0) for j in range(num_books)] for i in range(num_books)]
            
        vectorizer = TextVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
        if tfidf_matrix is None or tfidf_matrix.shape[0] == 0:
            num_books = len(self.books)
            return [[(1.0 if i == j else 0.0) for j in range(num_books)] for i in range(num_books)]
        
        return cosine_similarity(tfidf_matrix) # 使用sklearn的余弦相似度

    def recommend(self, user, n=5):
        """为用户推荐内容相似的书籍"""
        # 找到用户评分高或喜欢的书籍作为种子
        # 这里简化为使用用户的偏好类别下的书籍，或者用户评分过的书籍
        seed_books_indices = []
        for book_id, rating in user.ratings.items():
            if rating >= 4: # 假设4分及以上为喜欢
                if book_id in self.book_index_map:
                    seed_books_indices.append(self.book_index_map[book_id])
        
        if not seed_books_indices and user.preferences:
            # 如果没有高分书籍，尝试使用偏好类别中的书籍作为种子
            for book in self.books:
                if book.category in user.preferences and book.book_id in self.book_index_map:
                    seed_books_indices.append(self.book_index_map[book.book_id])
                    if len(seed_books_indices) > 5: # 取少量种子即可
                        break
        
        if not seed_books_indices:
            return [] # 没有种子书籍，无法进行内容推荐

        # 计算候选书籍的平均相似度
        candidate_scores = {}
        for i in range(len(self.books)):
            if self.books[i].book_id not in user.ratings: # 未评分的书籍
                avg_sim = 0
                for seed_idx in seed_books_indices:
                    avg_sim += self.similarity_matrix[seed_idx][i]
                if seed_books_indices: # 避免除以零
                    avg_sim /= len(seed_books_indices)
                candidate_scores[self.books[i]] = avg_sim
        
        # 按相似度排序并返回top N
        sorted_candidates = sorted(candidate_scores.items(), key=lambda item: item[1], reverse=True)
        return [book for book, score in sorted_candidates[:n]]