import uuid
import logging
from .states import ClassificationResult, ClassifierAgentState, MessageResponse
from langgraph.graph import StateGraph, END
from ..messages import EmailMessage, WhatsappMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

class Graph:
    def __init__(self, command, outgoing_mailbox, db_manager):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        self.command = command
        self.outgoing_mailbox = outgoing_mailbox
        self.db_manager = db_manager
    
    def email_ingestion_node(self, state: ClassifierAgentState) -> ClassifierAgentState:
        try:
            with open(state['path'], "r") as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line.startswith("message:"):
                    type = line.split(":")[1].strip()
                    state['type'] = type
                elif line.startswith("sender:"):
                    sender = line.split(":")[1].strip()
                elif line.startswith("subject:"):
                    if type == 'email':
                        subject = line.split(":")[1].strip()
                elif line.startswith("body:"):
                    body = line.split(":", 1)[1].strip()
                elif line.startswith("timestamp:"):
                    timestamp = line.split(":")[1].strip()
                elif line.startswith("name:"):
                    name = line.split(":")[1].strip()
            if type == "email":
                message = EmailMessage(
                    name=name,
                    subject=subject,
                    body=body,
                    sender=sender,
                    timestamp=timestamp
                )
            elif type == "whatsapp":
                message = WhatsappMessage(
                    name=name,
                    body=body,
                    sender=sender,
                    timestamp=timestamp
                )
            state['user_id'] = self.db_manager.generate_user_id(
                username=name,
                user_sender_address=sender
            )
            state['message'] = message
            state['action'] = f"Message from {message.sender} ingested successfully."
            self.db_manager.log_agent_action(
                action=state['action'],
                user_id=state['user_id']
            )
            logging.info(f"Message from {message.sender} ingested successfully.")
            return state
        except Exception as e:
            logging.error(f"Failed to ingest email: {e}")
            raise ValueError(f"Email ingestion is not enabled: {e}")
    
    def send_email_node(self, state: ClassifierAgentState) -> ClassifierAgentState:
        if state['classification_result'].category != "Spam":
            filename = str(uuid.uuid4())
            with open(f"{self.outgoing_mailbox}/{filename}.txt", "w") as f:
                f.write(f"To: {state['message'].sender}\n")
                f.write(f"Subject: {state['classification_result'].category} Query Automated Response\n")
                f.write(f"Body: {state['response']}\n")
            state['action'] = f"Email sent to {state['message'].sender} with filename {filename}.txt"
        else:
            state['action'] = f"No email sent to {state['message'].sender} as the message was classified as Spam."
            logging.info(f"No email sent to {state['message'].sender} as the message was classified as Spam.")
        self.db_manager.log_agent_action(
            action=state['action'],
            user_id=state['user_id']
        )
        return state
    
    def classification_node(self, state: ClassifierAgentState) -> ClassifierAgentState:
        system_template = """
You are an expert message classifier. Your task is to categorize messages into one of the following categories:
- 'Support': For customer inquiries, bug reports, or requests for help.
- 'Sales': For sales inquiries, product information requests, or partnership opportunities.
- 'Marketing': For marketing-related messages, newsletters, or promotional content.
- 'Spam': For unsolicited messages, advertisements, or phishing attempts.
- 'General': For messages that do not fit into the above categories.

You will provide a classification of the message based on the provided categories.
You will provide a brief reason for your classification.
You will provide  a confidence level for your classification on a scale of 1 to 10, where 10 is very confident and 1 is not confident at all."""
        human_template = "From: {sender}\nUser's name: {name}\nMessage body: {body}"
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)

        prompt = ChatPromptTemplate(messages=[system_message, human_message])
        chain = prompt | self.command.with_structured_output(ClassificationResult)
        try:
            classification_result = chain.invoke({
                "sender": state['message'].sender,
                "name": state['message'].name,
                "body": state['message'].body
            })
            state['classification_result'] = classification_result
            state['action'] = 'Classification completed successfully'
            logging.info(f"Message sent by {state['message'].sender} classified as {classification_result.category} with confidence {classification_result.confidence}.")
        except Exception as e:
            state['classification_result'] = None
            state['action'] = f'Classification failed: {e}'
            logging.error(f"Classification failed: {e}")
        self.db_manager.log_agent_action(
            action=state['action'],
            user_id=state['user_id']
        )
        self.db_manager.log_user_status(
            user_id=state['user_id'],
            username=state['message'].name,
            user_sender_address=state['message'].sender,
            platform=state['type'],
            agent_action_id=self.db_manager.agent_actions_db.iloc[-1]['agent_action_id'],
            status=state['classification_result'].category if state['classification_result'] else 'Failed'
        )
        return state
    
    def response_node(self, state: ClassifierAgentState) -> ClassifierAgentState:
        system_template = """
You are a message router based on message classification. Your task is to send an appropriate response to the user based on the classification.
- If the classification is 'Support', you will give a preliminary response and direct them to email: khaled.ibrahim@wfp.org for more information.
- If the classification is 'Sales', you will give a preliminary response based on your knowledge and direct them to send an email to khaledhamza@aucegypt.edu for more information.
- If the classification is 'Marketing', you will let them know that our marketing department is still under development and that they should reach out 3 months later.
- If the classification is 'Spam', provide no email response.
- If the classification is 'General', you will provide a general response and direct them to email: khaledamr2005@gamil.com for more general inquiries.

In summary, given a message and a classification, you will provide an response message based on the rules above.
This message should be concise and to the point, providing the user with the necessary information and the next steps.
The response should be in the format of a formal email response addressing the user by their name and identifying yourself as the sender of the message. You should identify yourself as Khaled Command-R, a virtual assistant for the Agentic CRM system."""
        human_template = "Username:{name}\nMessage body: {body}\nClassification: {classification}"
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)

        prompt = ChatPromptTemplate(messages=[system_message, human_message])
        chain = prompt | self.command.with_structured_output(MessageResponse)
        try:
            response = chain.invoke({
                "name": state['message'].sender,
                "body": state['message'].body,
                "classification": state['classification_result']
            })
            state['response'] = response
            state['action'] = 'Response generated successfully'
            logging.info(f"A response has been generated for the message sent by {state['message'].sender} dated {state['message'].timestamp}.")
        except Exception as e:
            state['action'] = f"Response generation failed: {e}"
            logging.error(f"Response generation failed: {e}")
        self.db_manager.log_agent_action(
            action=state['action'],
            user_id=state['user_id']
        )
        return state
    
    def build(self) -> StateGraph:
        workflow = StateGraph(ClassifierAgentState)
        workflow.add_node(
            "email_ingestion",
            self.email_ingestion_node
        )
        workflow.add_node(
            "classification_node",
            self.classification_node
        )
        workflow.add_node(
            "response_node",
            self.response_node
        )
        workflow.add_node(
            "send_email",
            self.send_email_node
        )
        workflow.set_entry_point("email_ingestion")
        workflow.add_edge("email_ingestion", "classification_node")
        workflow.add_edge("classification_node", "response_node")
        workflow.add_edge("response_node", "send_email")
        workflow.add_edge("send_email", END)
        graph = workflow.compile()
        return graph