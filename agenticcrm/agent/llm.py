import logging
from langchain_cohere import ChatCohere
from .states import ClassifierAgentState

class LLM:
    def __init__(self, cohere_api_key: str = None):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        try:
            self.command = ChatCohere(
                model='command-r-plus',
                cohere_api_key=cohere_api_key,
                temperature=0.0
            )
            logging.info("Cohere's command-r-plus initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize ChatCohere: {e}")
            raise
        
        self.state: ClassifierAgentState = {
            'user_id': None,
            'path': None,
            'message': None,
            'type': None,
            'classification_result': None,
            'response': None,
            'action': None
        }
    
    def reinitialize_state(self):
        self.state = {
            'user_id': None,
            'path': None,
            'message': None,
            'type': None,
            'classification_result': None,
            'response': None,
            'action': None
        }