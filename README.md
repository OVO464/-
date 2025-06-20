本系统由714独立开发，未经允许请勿转载
本资源可免费获得，如果你是付费得来，那恭喜你被骗了
本系统启动请直接运行main.py文件

您可以通过以下安装命令来安装所有必须的第三方库：
pip install Pillow openai scikit-learn numpy scipy nltk

使用本系统请保证电脑中安装了一下python库：
- Pillow (在代码中通过 from PIL import Image, ImageTk 导入): 用于图像处理，例如在GUI中显示图片。
- 安装命令: pip install Pillow

- openai : 用于与 DeepSeek API 进行交互，实现AI对话功能。
- 安装命令: pip install openai

- scikit-learn (在代码中通过 from sklearn... 导入，例如 TfidfVectorizer , cosine_similarity ): 一个强大的机器学习库，项目中用于文本向量化和计算余弦相似度。
- 安装命令: pip install scikit-learn

- numpy : scikit-learn 和其他科学计算库通常依赖于 numpy 进行高效的数值运算。虽然代码中可能没有直接 import numpy ，但 sklearn 会用到它。
- 安装命令: pip install numpy (如果 scikit-learn 安装时没有自动安装)

- scipy (在代码中通过 from scipy.sparse import csr_matrix 导入): 用于科学和技术计算，项目中用于创建稀疏矩阵。
- 安装命令: pip install scipy

- nltk (Natural Language Toolkit): 用于自然语言处理任务，如分词、去除停用词等。
- 安装命令: pip install nltk
- 注意： 首次使用 nltk 的某些功能时，可能还需要下载额外的数据包。例如，代码中注释掉了 nltk.download('punkt') 和 nltk.download('stopwords') 。如果运行时提示缺少这些资源，您需要在Python环境中执行这些下载命令一次。


# -
基于python开发的智能图书推荐系统(甚至没有前端以及使用到数据库OVO)
