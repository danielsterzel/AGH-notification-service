from pydantic import BaseModel


class Email(BaseModel):
    subject: str
    html: str
