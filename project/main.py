import os
from flask import Flask,render_template,request,jsonify
import requests
from chroma_test import retrieve_knowledge,embedding_model,client

#flask应用初始化 name会自动识别templates文件夹
app=Flask(__name__)

#配置deepseek llm
Deepseek_api_key="Bearer sk-aca7d680db034e5b87dc810e081c3158"
Deepseek_url="https://api.deepseek.com/v1/chat/completions"

#回答函数：检索知识库+调用llm生成回答
def rag_qa(question):
    #step1:调用已有检索函数 获取知识库文档 复用chroma_test.py
    related_docs=retrieve_knowledge(question)
    if not related_docs:
        return "未检索到相关知识库内容，无法回答你的问题",[]
    #step2:拼接相关文档为上下文（让LLM参考知识库回答）
    context=""
    for idx,(doc_content,similarity) in enumerate(related_docs,1):
        context +=f"参考文档{idx}(相似度:{similarity:.4f}):{doc_content}\n"
    #step3:构造llm提示词 让llm只基于上下文回答
    prompt = f"""
        你是一个基于知识库的智能问答助手，必须严格按照以下规则回答：
        1. 只能使用提供的参考文档内容回答问题，不能编造外部信息；
        2. 如果参考文档没有相关信息，直接回复"未检索到相关知识库内容，无法回答你的问题。"；
        3. 回答要简洁明了，分点说明（如果需要），不要冗余；
        4. 不要提及"参考文档"等字样，直接给出自然的回答
        
        参考文档:
        {context}
        
        用户问题：{question}
        """

    #step4:调用deepseek api生成回答
    headers={
        "Content-Type":"application/json",
        "Authorization":f"Bearer sk-aca7d680db034e5b87dc810e081c3158"
    }
    data={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 500,
        #回答最大长度
        "temperature": 0.3
        #回答严谨度
    }

    try:
       #发送请求到deepseek api
       response=requests.post("https://api.deepseek.com/v1/chat/completions",headers=headers,json=data,timeout=30)
       response.raise_for_status()
       #抛出http错误
       answer=response.json()["choices"][0]["message"]["content"].strip()
       return answer,related_docs
    except Exception as e:
       print(f"LLM 调用失败：{str(e)}")
       return f"LLM 调用失败：{str(e)}", related_docs

#step5:web路由 首页展示html界面
@app.route("/")
def index():
    return render_template("index.html")

#step6:api接口 处理前端的问答请求
@app.route("/api/qa",methods=["POST"])
def api_qa():
    #获取前端传递的问题
    request_data=request.get_json()
    question=request_data.get("question","").strip()

    if not question:
        return jsonify({"error": "请输入有效的问题！"}), 400

    # 调用核心问答函数
    answer, related_docs = rag_qa(question)

    # 格式化相关文档（给前端展示）
    formatted_docs = [
        {"content": doc, "similarity": round(similarity, 4)}
        for doc, similarity in related_docs
    ]

    # 返回 JSON 结果给前端
    return jsonify({
        "question": question,
        "answer": answer,
        "related_docs": formatted_docs
    })
# step7. 启动 Web 服务
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)