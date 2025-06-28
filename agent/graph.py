import uuid
import logging
from .states import ClassifierAgentState
from langgraph.graph import StateGraph, END
from ..messages import EmailMessage, WhatsappMessage

class Graph:
    def __init__(self, outgoing_mailbox):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.outgoing_mailbox = outgoing_mailbox
    
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
            state['message'] = message
            state['action'] = f"Message from {message.sender} ingested successfully."
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
            return state
    
    def build(self) -> StateGraph:
        workflow = StateGraph(ClassifierAgentState)
        workflow.add_node(
            "email_ingestion",
            self.email_ingestion_node
        )
        workflow.add_node(
            "classification_node",
            self.llm.classification_node
        )
        workflow.add_node(
            "response_node",
            self.llm.response_node
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