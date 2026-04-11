from pydantic import BaseModel


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str

    class Config:
        from_attributes = True