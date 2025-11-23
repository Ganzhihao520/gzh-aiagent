import chromadb
from chromadb.utils import embedding_functions
# 第一步：配置国内镜像（放在最顶部，优先于所有导入）
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 阿里云国内镜像站，无需代理
os.environ["TRANSFORMERS_OFFLINE"] = "0"
import warnings
# 过滤 pkg_resources 相关的弃用警告
warnings.filterwarnings("ignore", category=UserWarning, message="pkg_resources is deprecated.*")
# 配置中文适配的嵌入函数 使用支持中文的Sentence-bert模型
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # 多语言模型，支持中文/英文，轻量高效
    # 若需更好的中文效果，可替换为："paraphrase-multilingual-MiniLM-L12-v2"（精度更高，速度稍慢）
)



import chromadb
from sentence_transformers import SentenceTransformer
# 第三步：加载模型（自动从国内镜像下载，速度快，无超时）
print("开始加载模型（国内镜像加速）...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("模型加载成功！")
#连接chroma服务
client=chromadb.HttpClient(host="localhost",port=8000)

#1.创建知识库集合（类似数据库的表）
collection=client.create_collection(
    name="knowledge_base",
    get_or_create=True,
embedding_function=sentence_transformer_ef
)

#2.准备知识数据库(从TXT文件导入数据库知识)
knowledge_data=[]
with open("E:\\aiagent\\knowledge.txt","r",encoding="utf-8") as f:
     for line in f:
         line=line.strip()
         if line:
             knowledge_data.append(line)
print(f"从 TXT 读取到 {len(knowledge_data)} 条知识库数据")  # 验证读取是否成功
# 3.插入数据到chroma
if knowledge_data:  # 只有读取到数据才插入
    document_embeddings = embedding_model.encode(knowledge_data).tolist()
    # 清空旧数据，插入新数据
    if collection.count() > 0:
        collection.delete(ids=collection.get()["ids"])
    collection.add(
        documents=knowledge_data,
        embeddings=document_embeddings,
        ids=[f"doc_{i}" for i in range(len(knowledge_data))]
    )
    print(f"成功插入 {len(knowledge_data)} 条数据到 Chroma")
    print(f"当前集合数据量：{collection.count()}")  # 再次验证插入后的数据量
else:
    print("未从 knowledge.txt 读取到有效数据，跳过插入")

#4.实现检索功能（用户问题 找相似知识库内容）
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

#测试检索
if __name__ == '__main__':
    while True:
        user_question = input("\n请输入你的问题（输入 'q' 退出）：")
        if user_question.lower() == 'q':
            break
        if not user_question.strip():
            print("请输入有效的问题！")
            continue
        similar_docs_with_distance = retrieve_knowledge(user_question)
        # 打印结果（显示相似度，验证是否准确）
        print(f"\n检索到的相关知识库内容（相似度越小越相关）：")
        if similar_docs_with_distance:
            for idx, (doc, distance) in enumerate(similar_docs_with_distance, 1):
                print(f"{idx}. 内容：{doc}")
                print(f"   相似度：{distance:.4f}")
        else:
            print("未检索到相关知识库内容，请尝试其他问题！")