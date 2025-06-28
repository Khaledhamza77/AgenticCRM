import logging
from langchain_cohere import ChatCohere
from .states import ClassifierAgentState

class LLM:
    def __init__(self, cohere_api_key: str = None):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
        try:
            self.command = ChatCohere(
                model='command-r-plus',
                cohere_api_key=cohere_api_key,
                temperature=0.0
            )
            logging.info("AnthropicLLM initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize AnthropicLLM: {e}")
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