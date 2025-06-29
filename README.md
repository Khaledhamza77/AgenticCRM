# Agentic Customer Relations Management (CRM) Message Classifier and Response Generator

## Overview
The Agentic Customer Relations Management (CRM) Message Classifier is a powerful Python package designed to intelligently classify and respond to incoming customer communications. Built leveraging the advanced capabilities of LangChain and LangGraph, and powered by Cohere's Command-R-Plus large language model, this system automates the routing and initial handling of customer inquiries.

Whether your customers reach out via email or WhatsApp, this agentic system ensures messages are accurately categorized and then generates appropriate responses.

## Features
- **Intelligent Message Classification**: Automatically classifies incoming messages into one of the following categories:
    - General
    - Sales
    - Marketing
    - Support
    - Spam
- **Automated Response Generation**: Based on the classification, the agent crafts and sends a tailored response.
- **Outgoing Mailbox Management**: All generated responses are neatly saved in the customer_relations_management/outgoing_mailbox directory.
- **Comprehensive Data Logging**:
    - User status is maintained in customer_relations_management/user_status.csv.
    - A detailed log of agent actions is recorded in customer_relations_management/agent_actions.csv, serving as the package's operational database.
    - Flexible Communication Channels: Handles both email and WhatsApp text message formats.

- **Powered by Advanced AI**: Leverages the sophisticated natural language understanding and generation of Cohere's Command-R-Plus model, orchestrated by LangChain and LangGraph.

## Installation
To get started with the Agentic CRM Message Classifier, you can install it directly from its GitHub repository using pip.
1. Ensure Git is installed on your system
2. Install agenticcrm package using the following code:
```bash
pip install git+https://github.com/Khaledhamza77/AgenticCrm.git
```
This command will install the agenticcrrm package and all its required dependencies listed in requirements.txt.

## Setup and Usage
Before running the application, you need to set up your Cohere API key and prepare your incoming messages.

1. Create a plain text file named `cohere_api_key.txt` in your working directory (the directory from which you will run your Python script). This file should contain only your Cohere API key. Visit [LangChain+Cohere API documentation](https://python.langchain.com/docs/integrations/providers/cohere/#chat) for more information.

2. Prepare Incoming Messages
The agent processes messages from .txt files. Create a folder (e.g., incoming_messages) in your working directory and place your message files inside it. Each message file should be a .txt file formatted as follows:
    
    Example Message File (message1.txt):
```bash
    message: email
    sender: john@example.com
    subject: Question about my billing for subscription
    name: John Doe
    body: I was charged twice this month, can you please look into it?
    timestamp: 2025-06-28 14:15:00
```
    - message: Can be email or whatsapp.
    - sender: The sender's email or phone number.
    - subject: (Optional for WhatsApp) The subject of the message.
    - name: The sender's name.
    - body: The main content of the message.
    - timestamp: The time the message was received (format: YYYY-MM-DD HH:MM:SS).

3. **Run the Application**: Once your API key is set up and messages are prepared, you can run the CRM application from your Python script:
```python
from agenticcrrm.crm import CRM_application
# Assuming your message files are in a folder like 'incoming_messages'
# You would likely have a loop or logic to read these files and feed them to the CRM_application
# For demonstration, CRM_application().run() expects to find these files based on its internal logic.
# Make sure your 'customer_relations_management' folder will be created in the current working directory.

if __name__ == "__main__":
    app = CRM_application()
    app.run()
```
4. Expected Output: When you run CRM_application().run(), the following actions will occur:
    - Messages from the designated input folder will be read.
    - The agent will classify each message (General, Sales, Marketing, Support, Spam).
    - An appropriate response will be generated for each classified message.
    - Responses will be saved in customer_relations_management/outgoing_mailbox.
    - user_status.csv and agent_actions.csv will be updated/created in the customer_relations_management folder.

## Package Structure

```bash
AgenticCrm/
├── __init__.py
├── crm.py
├── messages.py
├── data.py
├── agent/
│   ├── __init__.py
│   ├── graph.py
│   └── llm.py
│   └── states.py
├── setup.py
├── requirements.txt
└── README.md
```