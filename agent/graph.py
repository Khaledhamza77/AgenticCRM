import uuid
from .states import ClassifierAgentState
from langgraph.graph import StateGraph, END
from messages import EmailMessage, WhatsappMessage

class Graph:
    def __init__(self, llm, tobesent_mailbox):
        self.llm = llm
        self.tobesent_mailbox = tobesent_mailbox
    
    def email_ingestion_node(self, message: EmailMessage | WhatsappMessage) -> ClassifierAgentState:
        try:
            self.llm.state.message = message
            return self.llm.state
        except Exception as e:
            raise ValueError(f"Email ingestion is not enabled: {e}")
    
    def send_email_node(self):
        filename = str(uuid.uuid4())
        with open(f"{self.tobesent_mailbox}/{filename}.txt", "w") as f:
            f.write(f"To: {self.llm.state.message.sender}\n")
            f.write(f"Subject: {self.llm.state.classification_result.category} Query Automated Response\n")
            f.write(f"Body: {self.llm.state.action}\n")
        self.llm.state.action = f"Email sent to {self.llm.state.message.sender} with filename {filename}.txt"
        return self.llm.state
    
    def build(self) -> StateGraph:
        workflow = StateGraph(self.llm.state)
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