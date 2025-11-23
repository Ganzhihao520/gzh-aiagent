import requests
import chromadb
from chromadb.utils import embedding_functions
# 第一步：配置国内镜像（放在最顶部，优先于所有导入）
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 阿里云国内镜像站，无需代理
os.environ["TRANSFORMERS_OFFLINE"] = "0"

import chromadb
from sentence_transformers import SentenceTransformer
# 第二步：加载模型（自动从国内镜像下载，速度快，无超时）
print("开始加载模型（国内镜像加速）...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("模型加载成功！")
#连接chroma服务
client=chromadb.HttpClient(host="localhost",port=8000)

# 弃用警告
import warnings
# 过滤 pkg_resources 相关的弃用警告
warnings.filterwarnings("ignore", category=UserWarning, message="pkg_resources is deprecated.*")
# 配置中文适配的嵌入函数 使用支持中文的Sentence-bert模型
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # 多语言模型，支持中文/英文，轻量高效
    # 若需更好的中文效果，可替换为："paraphrase-multilingual-MiniLM-L12-v2"（精度更高，速度稍慢）
)

#连接chroma向量数据库
chroma_client=chromadb.HttpClient(host="localhost",port=8000)
collection=chroma_client.get_collection(name="knowledge_base")

#大模型api
Deepseek_api_key="Bearer sk-aca7d680db034e5b87dc810e081c3158"
Deepseek_url="https://api.deepseek.com/v1/chat/completions"

#检索函数
def retrieve_knowledge(question):
    # 生成问题向量
    query_embedding = embedding_model.encode(question).tolist()
    #检索相似度最高的2条结果
    results=collection.query(
        query_embeddings=[query_embedding],
        n_results=2,
        include=["documents","distances"]
    #返回检索的文本内容
    )
    # 1. 获取文档列表（处理 None 和空列表）
    documents_list = results.get("documents")  # 先获取整个 documents 字段（可能是 None）
    retrieved_docs = []
    if documents_list is not None and len(documents_list) > 0:
        retrieved_docs = documents_list[0] or []  # 取第一个查询的结果，为空则设为空列表

    # 2. 获取相似度列表（处理 None 和空列表）
    distances_list = results.get("distances")  # 先获取整个 distances 字段（可能是 None）
    retrieved_distances = []
    if distances_list is not None and len(distances_list) > 0:
        retrieved_distances = distances_list[0] or []  # 同上

    # 打印 results 结构（帮你确认 Chroma 返回格式，可选但推荐）
    print("\n Chroma 查询原始结果：")
    print(f"documents 字段：{documents_list}")
    print(f"distances 字段：{distances_list}")

    # 确保文档和相似度列表长度一致
    min_len = min(len(retrieved_docs), len(retrieved_distances))
    return list(zip(retrieved_docs[:min_len], retrieved_distances[:min_len]))

    #大模型生成函数 优化提示词 结合检索结果
def generate_answer(question,retrieved_docs):
    #构造提示词，让大模型基于检索结果回答
    prompt = f"""
        你是智能问答助手，必须基于以下知识库内容回答用户问题，禁止编造信息：
        知识库内容：{retrieved_docs}
        如果知识库中没有相关信息，直接回复“暂无相关答案，请补充知识库内容后再试”。
        用户问题：{question}
        回答要求：简洁明了，不超过3句话。
        """
    headers = {
        "Content-Type": "application/json",  # 指定请求的数据格式
        "Authorization": "Bearer sk-aca7d680db034e5b87dc810e081c3158"
        #     api密钥
    }
    # 构造请求参数
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 200,
        #     回答最大长度
        "temperature": 0.3
        # 回答严谨度
    }
    response = requests.post("https://api.deepseek.com/v1/chat/completions", json=payload, headers=headers)
    return response.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    print("智能问答系统已启动（输入'退出'结束）：")
    while True:
        user_question = input("你：")
        if user_question == "退出":
            break
        # 1. 检索相关知识
        similar_docs = retrieve_knowledge(user_question)
        # 2. 生成回答
        answer = generate_answer(user_question, similar_docs)
        print(f"助手：{answer}\n")