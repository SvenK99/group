import configparser
import requests
import os
class HKBU_ChatGPT():
    def __init__(self, config=None):
            # 直接从环境变量读取
        self.config= {'CHATGPT':{
            'BASICURL': os.environ.get("CHATGPT_BASICURL",'https://genai.hkbu.edu.hk/general/rest'),
            'MODELNAME': os.environ.get("CHATGPT_MODELNAME",'gpt-4-o-mini'),
            'APIVERSION': os.environ.get("CHATGPT_APIVERSION",'2024-05-01-preview'),
            'ACCESS_TOKEN': os.environ.get("ACCESS_TOKEN_CHATGPT")
            }
        }


        # 检查必要配置项
        required_keys = ['BASICURL', 'MODELNAME', 'APIVERSION', 'ACCESS_TOKEN']
        for key in required_keys:
            if not self.config['CHATGPT'].get(key):
                raise ValueError(f"缺失必要配置项: {key}")


    def submit(self,message):
        conversation = [{"role": "user", "content": message}]
        url = (self.config['CHATGPT']['BASICURL']) + "/deployments/" + (self.config['CHATGPT']['MODELNAME']) +"/chat/completions/?api-version=" +(self.config['CHATGPT']['APIVERSION'])
        headers = { 'Content-Type': 'application/json',
        'api-key': os.environ.get("ACCESS_TOKEN_CHATGPT") }
        payload = { 'messages': conversation }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response
if __name__ == '__main__':
    ChatGPT_test = HKBU_ChatGPT()
    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)