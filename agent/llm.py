import logging
from langchain_anthropic import AnthropicLLM
from .states import ClassificationResult, ClassifierAgentState, MessageResponse

class LLM:
    def __init__(self, anthropic_api_key: str = None):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
        try:
            self.claude = AnthropicLLM(
                model='claude-3-7-sonnet-20250219',
                anthropic_api_key=anthropic_api_key,
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