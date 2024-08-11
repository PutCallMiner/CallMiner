from beanie import Document

from be.schemas import Person


class PersonDB(Document):
    fname: str
    lname: str

    class Settings:
        name = "persons"
