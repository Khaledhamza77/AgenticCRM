import uuid
import logging
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self, root: str):
        self.root = root
        self.agent_actions_db = pd.read_csv(f"{root}/customer_relations_management/agent_actions.csv") if pd.io.common.file_exists(f"{root}/customer_relations_management/agent_actions.csv") else pd.DataFrame(columns=['agent_action_id', 'action', 'user_id', 'timestamp'])
        self.user_status_db = pd.read_csv(f"{root}/customer_relations_management/user_status.csv") if pd.io.common.file_exists(f"{root}/customer_relations_management/user_status.csv") else pd.DataFrame(columns=['user_id', 'username', 'user_sender_address', 'platform', 'agent_action_id', 'status'])

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def generate_user_id(self, username: str, user_sender_address: str):
        existing_user = self.user_status_db[
            (self.user_status_db['username'] == username) &
            (self.user_status_db['user_sender_address'] == user_sender_address)
        ]

        if not existing_user.empty:
            return existing_user.iloc[0]['user_id']
        else:
            return str(uuid.uuid4())
    
    def log_agent_action(self, action: str, user_id: str):
        new_action = pd.DataFrame([{
            'agent_action_id': len(self.agent_actions_db) + 1,
            'action': action,
            'user_id': user_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        self.agent_actions_db = pd.concat([self.agent_actions_db, new_action], ignore_index=True)
        logging.info(f"Logged agent action: {action} for user_id: {user_id}")
    
    def log_user_status(self, user_id: str, username: str, user_sender_address: str, platform: str, agent_action_id: int, status: str):
        if user_id in self.user_status_db['user_id'].values:
            self.user_status_db.loc[self.user_status_db['user_id'] == user_id, ['username', 'user_sender_address', 'platform', 'agent_action_id', 'status']] = [
            username, user_sender_address, platform, agent_action_id, status
            ]
        else:
            new_status = pd.DataFrame([{
                'user_id': user_id,
                'username': username,
                'user_sender_address': user_sender_address,
                'platform': platform,
                'agent_action_id': agent_action_id,
                'status': status
            }])
            self.user_status_db = pd.concat([self.user_status_db, new_status], ignore_index=True)
        logging.info(f"Logged user status for user_id: {user_id} with status: {status}")

    def database_sync(self):
        self.agent_actions_db.to_csv(f"{self.root}/customer_relations_management/agent_actions.csv", index=False)
        self.user_status_db.to_csv(f"{self.root}/customer_relations_management/user_status.csv", index=False)
        logging.info("Databases synchronized to CSV files.")