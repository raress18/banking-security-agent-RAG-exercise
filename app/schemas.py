from typing import Literal

from pydantic import BaseModel

class Transaction(BaseModel):
    id: str
    user_id: str
    card_id: str
    amount: float
    currency: str = "RON"
    merchant_raw: str
    status: Literal["pending", "settled"]
    city: str
    timestamp: str

class Card(BaseModel):
    id: str
    user_id: str
    last4: str
    status: Literal["active", "frozen"]
    freeze_reason: str | None = None

class MerchantInfo(BaseModel):
    merchant_raw: str
    clean_name: str
    category: str    
    risk_score: Literal["low", "medium", "high" ]
    notes: str
        
class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    risk_level: Literal["low", "medium", "high"]
    requires_confirmation: bool
    actions_taken: list[str]
    tools_executed: list[str]