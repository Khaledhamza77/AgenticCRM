from typing import TypedDict, Literal
from pydantic import Field, BaseModel
from messages import EmailMessage, WhatsappMessage

class MessageResponse(BaseModel):
    response: str = Field(
        description="The response message to be sent back to the user."
    )

class ClassificationResult(BaseModel):
    category: Literal["Support", "Sales", "Marketing", "General", "Spam"] = Field(
        description="The category of the classification result."
    )
    reason: str = Field(
        description="The reason for the classification decision."
    )
    confidence: str = Field(
        description="The confidence level of the classification result."
    )

class ClassifierAgentState(TypedDict):
    path: str | None
    message: EmailMessage | WhatsappMessage | None
    type: Literal["email", "whatsapp"] | None
    classification_result: ClassificationResult | None
    response: MessageResponse | None
    action: str | None