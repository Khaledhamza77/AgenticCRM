import os
import pandas as pd

class UserStatusDB:
    def __init__(self, db_path: str):
        if os.path.exists(db_path):
            self.db = pd.read_csv(db_path)
        else:
            self.db = pd.DataFrame(columns=['username', 'platform', 'status'])
            self.db.to_csv(db_path, index=False)
    
    def update_user_status(self, username: str, platform: str, llm_classification: str):
        if username in self.db['username'].values:
            self.db.loc[(self.db['username'] == username) and (self.db['platform'] == platform), 'status'] = llm_classification
        else:
            self.db = pd.concat([self.db, pd.DataFrame([{'username': username, 'platform': platform, 'status': llm_classification}])], ignore_index=True)
        self.db.to_csv('user_status.csv', index=False)