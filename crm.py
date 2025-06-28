import os
import shutil
import logging
from .agent.llm import LLM
from .agent.graph import Graph
from .data import UserLogsDB, UserStatusDB

class CRM_application:
    def __init__(self, visualize_graph: bool = True, outgoing_mailbox: str = "outgoing_mailbox"):
        self.root= os.getcwd().replace('\\', '/')
        self.local_dir = f"{self.root}/AgenticCRM"
        if os.path.exists(self.local_dir):
            shutil.rmtree(self.local_dir)
            os.makedirs(self.local_dir)
        else:
            os.makedirs(self.local_dir)
        self.outgoing_mailbox = f"{self.local_dir}/{outgoing_mailbox}"
        os.makedirs(self.outgoing_mailbox)

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        anthropic_api_key = self.get_anthropic_api_key()
        if anthropic_api_key:
            self.llm = LLM(anthropic_api_key=anthropic_api_key)
        else:
            logging.error("Cannot find anthropic_api_key.txt file in working directory.")

        self.graph = Graph(self.outgoing_mailbox).build()
        if visualize_graph:
            try:
                self.graph.visualize(filename="workflow_graph")
                logging.info("Workflow graph saved as workflow_graph.png")
            except Exception as e:
                logging.error(f"Failed to visualize workflow graph: {e}")
    
    def get_anthropic_api_key(self):
        api_key_path = os.path.join(self.root, 'anthropic_api_key.txt')
        if os.path.exists(api_key_path):
            with open(api_key_path, 'r') as file:
                return file.read().strip()
        else:
            logging.error("Anthropic API key not found.")
            return None
        
    def run(self):
        if not os.path.exists(f"{self.root}/incoming_messages"):
            logging.error("Incoming mailbox does not exist. Please create an 'incoming_messages' directory in the working directory.")
            return
        else:
            logging.info("Starting CRM application...")
            incoming_messages = f"{self.root}/incoming_messages"
            for filename in os.listdir(incoming_messages):
                if filename.endswith(".txt"):
                    path = f"{incoming_messages}/{filename}"
                    self.run_single(path)
                    self.llm.reinitialize_state()
        
    def run_single(self, path):
        self.llm.state['path'] = path
        self.graph.invoke(self.llm.state)