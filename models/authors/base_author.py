from pydantic import BaseModel


class BaseAuthor(BaseModel):
    name: str