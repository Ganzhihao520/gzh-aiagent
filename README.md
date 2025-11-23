# gzh-aiagent
智能问答系统  
技术栈：  
python作为开发语言，选用Flask作为pythonweb框架，Rag核心技术选用ChromaDB作为向量数据库，通过embedding_model，将用户问题、知识库文档转换为可计算的向量，选用Deepseek llm作为第三方大语言模型，通过api调用，基于检索到的数据库上下文生成回答，前端使用HTML模板（index.html）,端口号为8080，技术逻辑：Python + Flask（Web 服务）→ 接收用户问题 → 文本嵌入 → Chroma DB（检索相似文档）→ 拼接上下文 → requests 调用 Deepseek LLM → 生成回答 → 以 JSON 返回前端 → HTML 界面展示。  
环境配置：python3.13.5  
文件结构：  
project/  
├── main.py  # 主程序  
├── chroma_test.py  # 依赖文件（含Chroma初始化、检索函数）  
└── templates/    
    └── index.html # 前端界面  
├── konwledge.txt #知识文档  

启动步骤：1.在python虚拟环境中吗，启动一个独立的 Chroma DB 向量数据库服务  
![屏幕截图 2025-11-23 173615.png]https://github.com/Ganzhihao520/gzh-aiagent/blob/main/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202025-11-23%20173615.png  
2.运行main.py  
3.浏览器输入localhost:8080  
可得到如下智能问答系统  
![291ef7a8c28d4e78140972e86311f660.png](https://github.com/Ganzhihao520/gzh-aiagent/blob/main/291ef7a8c28d4e78140972e86311f660.png)
