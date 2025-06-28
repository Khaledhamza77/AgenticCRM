import uuid
import logging
from .states import ClassifierAgentState
from langgraph.graph import StateGraph, END
from ..messages import EmailMessage, WhatsappMessage

class Graph:
    def __init__(self, llm, outgoing_mailbox):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        self.llm = llm
        self.outgoing_mailbox = outgoing_mailbox
    
    def email_ingestion_node(self) -> ClassifierAgentState:
        try:
            with open(self.llm.state['path'], "r") as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line.startswith("message:"):
                    type = line.split(":")[1].strip()
                    self.llm.state['type'] = type
                    if type == "email":
                        message = EmailMessage()
                    elif type == "whatsapp":
                        message = WhatsappMessage()
                    else:
                        raise ValueError(f"Unknown message type: {type}")
                elif line.startswith("sender:"):
                    message.sender = line.split(":")[1].strip()
                elif line.startswith("subject:"):
                    if isinstance(message, EmailMessage):
                        message.subject = line.split(":")[1].strip()
                elif line.startswith("body:"):
                    message.body = line.split(":", 1)[1].strip()
                elif line.startswith("timestamp:"):
                    message.timestamp = line.split(":")[1].strip()
                elif line.startswith("name:"):
                    message.name = line.split(":")[1].strip()
            self.llm.state['message'] = message
            self.llm.state['action'] = f"Message from {message.sender} ingested successfully."
            logging.info(f"Message from {message.sender} ingested successfully.")
            return self.llm.state
        except Exception as e:
            logging.error(f"Failed to ingest email: {e}")
            raise ValueError(f"Email ingestion is not enabled: {e}")
    
    def send_email_node(self) -> ClassifierAgentState:
        if self.llm.state['classification_result'].category != "Spam":
            filename = str(uuid.uuid4())
            with open(f"{self.outgoing_mailbox}/{filename}.txt", "w") as f:
                f.write(f"To: {self.llm.state['message'].sender}\n")
                f.write(f"Subject: {self.llm.state['classification_result'].category} Query Automated Response\n")
                f.write(f"Body: {self.llm.state['response']}\n")
            self.llm.state['action'] = f"Email sent to {self.llm.state['message'].sender} with filename {filename}.txt"
            return self.llm.state
    
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