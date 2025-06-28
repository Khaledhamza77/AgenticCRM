import pandas as pd
from datetime import datetime

class UserLogsDB:
    def __init__(self, db_path: str):
        if pd.io.common.file_exists(db_path):
            self.db = pd.read_csv(db_path)
        else:
            self.db = pd.DataFrame(columns=['username', 'platform', 'action', 'timestamp'])
            self.db.to_csv(db_path, index=False)

    def log_user_action(self, username: str, platform: str, action: str):
        new_log = pd.DataFrame([{
            'username': username,
            'platform': platform,
            'action': action,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        self.db = pd.concat([self.db, new_log], ignore_index=True)
        self.db.to_csv('user_logs.csv', index=False)