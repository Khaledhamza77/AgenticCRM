import os
import shutil
import logging
from .agent.llm import LLM
from .agent.graph import Graph
from .data import DatabaseManager

class CRM_application:
    def __init__(self, visualize_graph: bool = True, outgoing_mailbox: str = "outgoing_mailbox"):
        self.root= os.getcwd().replace('\\', '/')
        self.local_dir = f"{self.root}/customer_relations_management"
        if os.path.exists(self.local_dir):
            shutil.rmtree(self.local_dir)
            os.makedirs(self.local_dir)
        else:
            os.makedirs(self.local_dir)
        self.outgoing_mailbox = f"{self.local_dir}/{outgoing_mailbox}"
        os.makedirs(self.outgoing_mailbox)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        cohere_api_key = self.get_cohere_api_key()
        if cohere_api_key:
            self.llm = LLM(cohere_api_key=cohere_api_key)
        else:
            logging.error("Cannot find cohere_api_key#.txt file in working directory.")

        self.db_manager = DatabaseManager(self.root)

        self.graph = Graph(self.llm.command, self.outgoing_mailbox, self.db_manager).build()
        if visualize_graph:
            from IPython.display import Image, display
            try:
                display(Image(self.graph.get_graph(xray=True).draw_mermaid_png()))
            except Exception:
                logging.error("Could not generate graph image. Install graphviz if you want to see it.")
    
    def get_cohere_api_key(self):
        api_key_path = os.path.join(self.root, 'cohere_api_key.txt')
        if os.path.exists(api_key_path):
            with open(api_key_path, 'r') as file:
                return file.read().strip()
        else:
            logging.error("Cohere API key not found.")
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
        self.db_manager.database_sync()