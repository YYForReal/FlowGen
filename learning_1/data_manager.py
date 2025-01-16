import json
import os
from datetime import datetime
from pathlib import Path

class DataManager:
    def __init__(self, data_dir="data"):
        """初始化数据管理器"""
        self.data_dir = Path(data_dir)
        self.users_file = self.data_dir / "users.json"
        self.conversations_file = self.data_dir / "conversations.json"
        self.reminders_file = self.data_dir / "reminders.json"
        
        # 确保数据目录存在
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化数据文件
        self._init_data_files()
        
    def _init_data_files(self):
        """初始化数据文件"""
        default_data = {
            self.users_file: {},
            self.conversations_file: {},
            self.reminders_file: []
        }
        
        for file_path, default_content in default_data.items():
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, ensure_ascii=False, indent=2)
    
    def _load_json(self, file_path):
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_json(self, file_path, data):
        """保存JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_user(self, user_data):
        """保存用户数据"""
        users = self._load_json(self.users_file)
        users[user_data['user_id']] = user_data
        self._save_json(self.users_file, users)
    
    def get_user(self, user_id):
        """获取用户数据"""
        users = self._load_json(self.users_file)
        return users.get(user_id)
    
    def delete_user(self, user_id):
        """删除用户数据"""
        users = self._load_json(self.users_file)
        if user_id in users:
            del users[user_id]
            self._save_json(self.users_file, users)
            return True
        return False
    
    def save_conversation(self, user_id, conversation_data):
        """保存对话历史"""
        conversations = self._load_json(self.conversations_file)
        if user_id not in conversations:
            conversations[user_id] = []
        conversations[user_id].append({
            'timestamp': datetime.now().isoformat(),
            **conversation_data
        })
        self._save_json(self.conversations_file, conversations)
    
    def get_user_conversations(self, user_id, limit=10):
        """获取用户的对话历史"""
        conversations = self._load_json(self.conversations_file)
        user_conversations = conversations.get(user_id, [])
        return user_conversations[-limit:] if limit else user_conversations
    
    def save_reminder(self, reminder_data):
        """保存提醒事项"""
        reminders = self._load_json(self.reminders_file)
        reminders.append({
            'id': len(reminders) + 1,
            'created_at': datetime.now().isoformat(),
            **reminder_data
        })
        self._save_json(self.reminders_file, reminders)
        return reminders[-1]['id']
    
    def get_user_reminders(self, user_id):
        """获取用户的提醒事项"""
        reminders = self._load_json(self.reminders_file)
        return [r for r in reminders if r['user_id'] == user_id]
    
    def update_reminder_status(self, reminder_id, status):
        """更新提醒事项状态"""
        reminders = self._load_json(self.reminders_file)
        for reminder in reminders:
            if reminder['id'] == reminder_id:
                reminder['status'] = status
                reminder['updated_at'] = datetime.now().isoformat()
                break
        self._save_json(self.reminders_file, reminders)
    
    def cleanup_old_conversations(self, days=30):
        """清理旧的对话记录"""
        conversations = self._load_json(self.conversations_file)
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for user_id in conversations:
            conversations[user_id] = [
                conv for conv in conversations[user_id]
                if datetime.fromisoformat(conv['timestamp']).timestamp() > cutoff_date
            ]
        
        self._save_json(self.conversations_file, conversations) 