import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# nltk.download('punkt') # 首次运行时可能需要下载
# nltk.download('stopwords')

def preprocess_text(text):
    """文本预处理：分词、去除停用词、词干提取等"""
    if not text: # 处理空文本的情况
        return ""
    tokens = nltk.word_tokenize(text.lower())
    stopwords = nltk.corpus.stopwords.words('english') # 或其他语言
    # 可以进一步进行词干提取或词形还原
    processed_tokens = [word for word in tokens if word.isalnum() and word not in stopwords]
    return " ".join(processed_tokens)

class TextVectorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None

    def fit_transform(self, documents):
        """对文档集合进行TF-IDF向量化"""
        processed_docs = [preprocess_text(doc) for doc in documents]
        self.tfidf_matrix = self.vectorizer.fit_transform(processed_docs)
        return self.tfidf_matrix

    def transform(self, documents):
        """对新文档进行TF-IDF转换 (使用已fit的vectorizer)"""
        processed_docs = [preprocess_text(doc) for doc in documents]
        return self.vectorizer.transform(processed_docs)

    def get_similarity_matrix(self):
        """计算TF-IDF矩阵的余弦相似度矩阵"""
        if self.tfidf_matrix is not None:
            return cosine_similarity(self.tfidf_matrix)
        return None

# 示例：假设Book对象有 description 属性
# book_descriptions = [book.description for book in all_books]
# vectorizer = TextVectorizer()
# book_tfidf_matrix = vectorizer.fit_transform(book_descriptions)
# book_similarity_matrix = vectorizer.get_similarity_matrix()
# book_similarity_matrix[i][j] 就是书i和书j基于描述的相似度