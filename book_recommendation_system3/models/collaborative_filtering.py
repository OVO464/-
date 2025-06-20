import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

class UserBasedCollaborativeFiltering:
    def __init__(self, users, books):
        self.users = users
        self.books = books
        self.user_id_map = {user.user_id: i for i, user in enumerate(users)}
        self.book_id_map = {book.book_id: i for i, book in enumerate(books)}
        self.n_users = len(users)
        self.n_books = len(books)
        self.user_item_matrix = self._create_user_item_matrix()
        self.user_similarity_matrix = self._calculate_user_similarity()

    def _create_user_item_matrix(self):
        """创建用户-物品评分矩阵 (稀疏矩阵)"""
        rows, cols, data = [], [], []
        for user_idx, user in enumerate(self.users):
            for book_id, rating in user.ratings.items():
                if book_id in self.book_id_map:
                    rows.append(user_idx)
                    cols.append(self.book_id_map[book_id])
                    data.append(rating)
        # 处理完全没有评分数据的情况
        if not data:
            return csr_matrix((self.n_users, self.n_books), dtype=np.float32)
        return csr_matrix((data, (rows, cols)), shape=(self.n_users, self.n_books), dtype=np.float32)

    def _calculate_user_similarity(self):
        """计算用户之间的相似度 (基于评分)"""
        if self.user_item_matrix.nnz == 0: # 如果矩阵全为0
             return np.identity(self.n_users) # 返回单位矩阵，表示用户只与自己相似
        # 注意：cosine_similarity 期望稠密矩阵或特定类型的稀疏矩阵
        # 如果用户数量很大，直接计算稠密矩阵可能会内存不足
        # 可以考虑使用 pairwise_distances_chunked 或其他优化方法
        return cosine_similarity(self.user_item_matrix)

    def recommend(self, target_user, n=5, k_neighbors=10):
        """为目标用户推荐书籍"""
        if target_user.user_id not in self.user_id_map:
            return [] # 用户不存在
        
        target_user_idx = self.user_id_map[target_user.user_id]
        
        if self.user_similarity_matrix is None or self.user_similarity_matrix.shape[0] == 0:
            return [] # 无法计算相似度
            
        user_similarities = self.user_similarity_matrix[target_user_idx]
        
        # 找到最相似的k个邻居 (排除自己)
        similar_users_indices = np.argsort(user_similarities)[::-1][1:k_neighbors+1]
        
        book_scores = defaultdict(float)
        books_weighted_sum_similarity = defaultdict(float)

        for neighbor_idx in similar_users_indices:
            neighbor_similarity = user_similarities[neighbor_idx]
            if neighbor_similarity <= 0: # 忽略不相似或负相关的用户
                continue
            
            # 获取邻居评分过的书籍 (稠密矩阵访问)
            # neighbor_ratings_sparse = self.user_item_matrix[neighbor_idx]
            # neighbor_rated_books_indices = neighbor_ratings_sparse.indices
            # neighbor_ratings_values = neighbor_ratings_sparse.data
            
            # 遍历所有书籍，看邻居是否评过分
            for book_idx in range(self.n_books):
                book_id_rev_map = {v: k for k, v in self.book_id_map.items()}
                current_book_id = book_id_rev_map.get(book_idx)

                # 目标用户未评分的书籍
                if current_book_id and current_book_id not in target_user.ratings:
                    neighbor_rating = self.user_item_matrix[neighbor_idx, book_idx]
                    if neighbor_rating > 0: # 邻居对这本书有过评分
                        book_scores[current_book_id] += neighbor_similarity * neighbor_rating
                        books_weighted_sum_similarity[current_book_id] += neighbor_similarity
        
        predicted_scores = {}
        for book_id, score_sum in book_scores.items():
            if books_weighted_sum_similarity[book_id] > 0:
                predicted_scores[self.books[self.book_id_map[book_id]]] = score_sum / books_weighted_sum_similarity[book_id]
            else:
                predicted_scores[self.books[self.book_id_map[book_id]]] = 0 # 避免除以零

        sorted_recommendations = sorted(predicted_scores.items(), key=lambda item: item[1], reverse=True)
        return [book for book, score in sorted_recommendations[:n]]