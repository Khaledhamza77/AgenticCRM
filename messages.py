from pydantic import BaseModel, Field

class WhatsappMessage(BaseModel):
    """WhatsApp message model."""
    body: str = Field(description="The text content of the WhatsApp message.")
    sender: str = Field(description="The phone number of the sender.")
    timestamp: str = Field(description="The time when the message was sent.", default=None)

class EmailMessage(BaseModel):
    """Email message model."""
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The body content of the email.")
    sender: str = Field(description="The email address of the sender.")
    timestamp: str = Field(description="The time when the email was sent.")