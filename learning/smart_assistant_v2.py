import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from prompts import (
    SYSTEM_PROMPT,
    REGISTERED_PROMPT,
    QUERY_PROMPT,
    DELETE_PROMPT,
    REMINDER_PROMPT,
    PERSONALIZATION_PROMPT
)
from data_manager import DataManager

# 加载环境变量
load_dotenv()
api_key = os.getenv('ZHIPU_API_KEY')
base_url = "https://open.bigmodel.cn/api/paas/v4/"
chat_model = "glm-4-flash"

# 创建OpenAI客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

class SmartAssistantV2:
    def __init__(self, current_user_id=None):
        self.client = client
        self.data_manager = DataManager()
        self.current_user_id = current_user_id
        
        # 基础提示词
        self.system_prompt = SYSTEM_PROMPT
        self.registered_prompt = REGISTERED_PROMPT
        self.query_prompt = QUERY_PROMPT
        self.delete_prompt = DELETE_PROMPT
        self.reminder_prompt = REMINDER_PROMPT
        self.personalization_prompt = PERSONALIZATION_PROMPT
        
        # 消息历史
        self.messages = {
            "system": [{"role": "system", "content": self.system_prompt}],
            "registered": [{"role": "system", "content": self.registered_prompt}],
            "query": [{"role": "system", "content": self.query_prompt}],
            "delete": [{"role": "system", "content": self.delete_prompt}],
            "reminder": [{"role": "system", "content": self.reminder_prompt}],
            "personalization": [{"role": "system", "content": self.personalization_prompt}]
        }
        
        # 当前处理状态
        self.current_assignment = "system"
        
        # 用户画像数据
        self.user_profile = {
            "preferences": {},  # 用户偏好
            "reminders": [],    # 提醒事项
            "history": []       # 历史交互
        }
        
        # 如果有用户ID，加载用户数据
        if self.current_user_id:
            self._load_user_data()

    def _load_user_data(self):
        """加载用户数据"""
        user_data = self.data_manager.get_user(self.current_user_id)
        if user_data:
            self.user_profile = user_data.get('profile', self.user_profile)
            
            # 加载最近的对话历史
            conversations = self.data_manager.get_user_conversations(self.current_user_id, limit=10)
            for conv in conversations:
                self.user_profile["history"].append({
                    "timestamp": conv["timestamp"],
                    "user_input": conv["user_input"],
                    "ai_response": conv["ai_response"]
                })
            
            # 加载提醒事项
            reminders = self.data_manager.get_user_reminders(self.current_user_id)
            self.user_profile["reminders"] = reminders

    def _save_user_data(self):
        """保存用户数据"""
        if self.current_user_id:
            user_data = {
                'user_id': self.current_user_id,
                'profile': self.user_profile,
                'updated_at': datetime.now().isoformat()
            }
            self.data_manager.save_user(user_data)

    def update_user_profile(self, user_input, ai_response):
        """更新用户画像"""
        # 更新内存中的历史记录
        self.user_profile["history"].append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response
        })
        
        # 保存到持久化存储
        if self.current_user_id:
            self.data_manager.save_conversation(
                self.current_user_id,
                {
                    "user_input": user_input,
                    "ai_response": ai_response
                }
            )
            self._save_user_data()

    def set_user_id(self, user_id):
        """设置当前用户ID并加载用户数据"""
        self.current_user_id = user_id
        self._load_user_data()

    def add_reminder(self, reminder_text, due_date):
        """添加提醒事项"""
        if not self.current_user_id:
            return None
            
        reminder_data = {
            'user_id': self.current_user_id,
            'text': reminder_text,
            'due_date': due_date,
            'status': 'pending'
        }
        
        reminder_id = self.data_manager.save_reminder(reminder_data)
        self.user_profile["reminders"].append(reminder_data)
        self._save_user_data()
        return reminder_id

    def get_response(self, user_input):
        # 添加用户输入到当前对话
        self.messages[self.current_assignment].append({"role": "user", "content": user_input})
        
        while True:
            response = self.client.chat.completions.create(
                model=chat_model,
                messages=self.messages[self.current_assignment],
                temperature=0.9,
                stream=False,
                max_tokens=2000,
            )

            ai_response = response.choices[0].message.content
            
            # 根据响应内容切换状态
            if "registered workers" in ai_response:
                self.current_assignment = "registered"
                print("意图识别:", ai_response)
                print("switch to <registered>")
                self.messages[self.current_assignment].append({"role": "user", "content": user_input})
            elif "query workers" in ai_response:
                self.current_assignment = "query"
                print("意图识别:", ai_response)
                print("switch to <query>")
                self.messages[self.current_assignment].append({"role": "user", "content": user_input})
            elif "delete workers" in ai_response:
                self.current_assignment = "delete"
                print("意图识别:", ai_response)
                print("switch to <delete>")
                self.messages[self.current_assignment].append({"role": "user", "content": user_input})
            elif "reminder workers" in ai_response:
                self.current_assignment = "reminder"
                print("意图识别:", ai_response)
                print("switch to <reminder>")
                self.messages[self.current_assignment].append({"role": "user", "content": user_input})
            elif "personalization workers" in ai_response:
                self.current_assignment = "personalization"
                print("意图识别:", ai_response)
                print("switch to <personalization>")
                self.messages[self.current_assignment].append({"role": "user", "content": user_input})
            elif "customer service" in ai_response:
                print("意图识别:", ai_response)
                print("switch to <customer service>")
                self.messages["system"] += self.messages[self.current_assignment]
                self.current_assignment = "system"
                self.update_user_profile(user_input, ai_response)
                return ai_response
            else:
                self.messages[self.current_assignment].append({"role": "assistant", "content": ai_response})
                self.update_user_profile(user_input, ai_response)
                return ai_response

    def start_conversation(self):
        print("Assistant: 您好！我是您的智能助手。我可以帮您处理账户相关事务，设置提醒，并记住您的偏好以提供更好的服务。")
        
        # 如果没有用户ID，先要求用户登录或注册
        if not self.current_user_id:
            print("Assistant: 请先登录或注册。您可以说\"我要注册\"或\"我要登录\"。")
        
        while True:
            user_input = input("User: ")
            if user_input.lower() in ['exit', 'quit']:
                # 保存最终的用户数据
                if self.current_user_id:
                    self._save_user_data()
                print("Assistant: 感谢您的使用，再见！")
                break
            
            response = self.get_response(user_input)
            print("Assistant:", response)

if __name__ == "__main__":
    # 设置当前用户ID
    current_user_id = input("请输入用户ID: ")
    assistant = SmartAssistantV2(current_user_id)
    assistant.start_conversation() 