# gzh-aiagent
智能问答系统
技术栈：
python作为开发语言，选用Flask作为pythonweb框架，Rag核心技术选用ChromaDB作为向量数据库，通过embedding_model，将用户问题、知识库文档转换为可计算的向量，选用Deepseek llm作为第三方大语言模型，通过api调用，基于检索到的数据库上下文生成回答，前端使用HTML模板（index.html）


