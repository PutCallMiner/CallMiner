from pydantic import BaseModel


class Person(BaseModel):
    fname: str
    lname: str
