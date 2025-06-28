import logging
from langchain_anthropic import AnthropicLLM
from .states import ClassificationResult, ClassifierAgentState, MessageResponse
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

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
            'message': None,
            'classification_result': None,
            'response': None,
            'action': None
        }
    
    def reinitialize_state(self):
        self.state = {
            'message': None,
            'classification_result': None,
            'response': None,
            'action': None
        }

    def classification_node(self) -> ClassifierAgentState:
        system_template = """
You are an expert message classifier. Your task is to categorize messages into one of the following categories:
- 'Support': For customer inquiries, bug reports, or requests for help.
- 'Sales': For sales inquiries, product information requests, or partnership opportunities.
- 'Marketing': For marketing-related messages, newsletters, or promotional content.
- 'Spam': For unsolicited messages, advertisements, or phishing attempts.
- 'General': For messages that do not fit into the above categories.

You will provide a classification of the message based on the provided categories.
You will provide a brief reason for your classification.
You will provide  a confidence level for your classification on a scale of 1 to 10, where 10 is very confident and 1 is not confident at all.
"""
        human_template = "Message body: {body}"
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)

        prompt = PromptTemplate.from_messages([system_message, human_message])
        chain = prompt | self.claude.with_structured_output(ClassificationResult)
        try:
            classification_result = chain.invoke({
                "body": self.state['message'].body
            })
            self.state['classification_result'] = classification_result
            self.state['action'] = 'Classification completed successfully'
            logging.info(f"Message sent by {self.state['message'].sender} classified as {classification_result.category} with confidence {classification_result.confidence}.")
        except Exception as e:
            self.state['classification_result'] = None
            self.state['action'] = f'Classification failed: {e}'
            logging.error(f"Classification failed: {e}")
        return self.state
    
    def response_node(self) -> ClassifierAgentState:
        system_template = """
You are a message router based on message classification. Your task is to send an appropriate response to the user based on the classification.
- If the classification is 'Support', you will give a preliminary response and direct them to email: khaled.ibrahim@wfp.org for more information.
- If the classification is 'Sales', you will give a preliminary response based on your knowledge and direct them to send an email to khaledhamza@aucegypt.edu for more information.
- If the classification is 'Marketing', you will let them know that our marketing department is still under development and that they should reach out 3 months later.
- If the classification is 'Spam', provide no email response.
- If the classification is 'General', you will provide a general response and direct them to email: khaledamr2005@gamil.com for more general inquiries.

In summary, given a message and a classification, you will provide an response message based on the rules above.
This message should be concise and to the point, providing the user with the necessary information and the next steps.
The response should be in the format of a formal email response addressing the user by their name and identifying yourself as the sender of the message. You should identify yourself as Khaled Claude, a virtual assistant for the Agentic CRM system."""
        human_template = "Username:{name}\nMessage body: {body}\nClassification: {classification}"
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)

        prompt = PromptTemplate.from_messages([system_message, human_message])
        chain = prompt | self.claude.with_structured_output(MessageResponse)
        try:
            response = chain.invoke({
                "name": self.state['message'].sender,
                "body": self.state['message'].body,
                "classification": self.state['classification_result']
            })
            self.state['response'] = response
            self.state['action'] = 'Response generated successfully'
            logging.info(f"A response has been generated for the message sent by {self.state['message'].sender} dated {self.state['message'].timestamp}.")
        except Exception as e:
            self.state['action'] = f"Response generation failed: {e}"
            logging.error(f"Response generation failed: {e}")
        return self.state