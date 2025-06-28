import logging
from langchain_openai import OpenAI
from .states import ClassifierAgentState

class LLM:
    def __init__(self, openai_api_key: str = None):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
        try:
            self.claude = OpenAI(
                model='gpt-4.1',
                openai_api_key=openai_api_key,
                temperature=0.0
            )
            logging.info("OpenAI initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI: {e}")
            raise
        
        self.state: ClassifierAgentState = {
            'path': None,
            'message': None,
            'classification_result': None,
            'response': None,
            'action': None
        }
    
    def reinitialize_state(self):
        self.state = {
            'path': None,
            'message': None,
            'classification_result': None,
            'response': None,
            'action': None
        }