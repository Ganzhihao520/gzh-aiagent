import requests
"""
调用大模型API
"""
def call_deepseek(question):
    #配置api信息
    url="https://api.deepseek.com/v1/chat/completions"
    headers={
        "Content-Type":"application/json", #指定请求的数据格式
        "Authorization":"Bearer sk-aca7d680db034e5b87dc810e081c3158"
    #     api密钥
    }
    # 构造请求参数
    payload={
        "model":"deepseek-chat",
        "messages":[{"role":"user","content":question}],
        "max_tokens":200,
    #     回答最大长度
        "temperature":0.3
    #回答严谨度
    }
    # 发送请求并获取结果
    response=requests.post(url,json=payload,headers=headers)
    # 关键：打印状态码和原始响应（先注释掉 json() 解析）
    # print("响应状态码：", response.status_code)
    # print("响应原始内容：", response.text)  # 看服务器到底返回了什么（是错误提示还是空内容）
    result=response.json()
    return  result["choices"][0]["message"]["content"]
#测试调用
if __name__ == '__main__':
    # user_question = "你好，测试一下 API 是否正常"
    # call_deepseek(user_question)
    user_question=input("请输入你的问题")
    answer=call_deepseek(user_question)
    print(f"回答：{answer}")
