from src.worker.worker import Worker
from src.data.database_element import Person

class KarmaTransactionWorker(Worker):
    keywords = ["karma"]

    def reply(self, message: str, sender_person: Person) -> str:
        """
        Transfer karma between persons, reply with a message
        """
        # identify receiver
        message_list = message.split()
        message_list.remove("karma")
        if len(message_list) == 0:
            return "For a karma transaction please also specify the name of the receiver and the amount e.g.: 'Paula 5 karma'"
        receiver_persons = self.data.find('persons', lambda person: person.name.lower() in message_list)
        if len(receiver_persons) != 1:
            return f"Couldn't identify exactly one person with the given keywords [{' | '.join([w for w in message_list])}], please choose one person from that list: {', '.join([person.name for person in self.data.find(attribute_name='persons')])}"
        receiver_person = receiver_persons[0]
        if sender_person == receiver_person:
            return f"Sorry, you cannot transfer karma to yourself. Please choose one person from that list: {', '.join([person.name for person in self.data.find(attribute_name='persons') if receiver_person != person])}\n]"
        
        # identify amount
        message_list.remove(receiver_person.name.lower())
        if len(message_list) == 0:
            return "For a karma transaction please also specify an amount e.g.: 'Paula 5 karma'"
        amount = None
        for word in message_list:
            if word.isdigit():
                amount = int(word)
                break
        if not amount:
            return f"I have not been able to find an integer positive transfer amount in keywords {', '.join([w for w in message_list])}. Please specify a transaction for example like that: 'Paula 5 karma'"
        
        # transaction
        sender_person.karma -= amount
        receiver_person.karma += amount
        confirmation_message = f"Transaction of {amount} karma from {sender_person.name} to {receiver_person.name} successful. \nNew karma balance: {', '.join([f'{person.name}: {person.karma}' for person in self.data.find('persons')])}"
        return confirmation_message
