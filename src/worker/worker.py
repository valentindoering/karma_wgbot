from src.data.data import Data, Person
from src.openai import OpenAi

class Worker():
    keywords = None # subclass responsibility

    def __init__(self, data: Data):
        self.data = data
    
    def is_triggered(self, message: str) -> bool:
        for keyword in self.keywords:
            if keyword in message.split():
                return True
        return False
    
    # Public: Subclass Responsibility --------------------------
    
    def reply(self, message: str, sender_person: Person) -> str:
        raise NotImplementedError
    
    # Private Utils ---------------------------------------------

    def _next_present_person(self, current_person: Person) -> Person:
        persons = self.data.find('persons')
        for i in range(1, len(persons)):
            new_assignee = persons[(current_person.id + i) % len(persons)]
            if new_assignee.is_present:
                return new_assignee
        return None