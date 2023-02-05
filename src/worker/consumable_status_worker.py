from src.worker.worker import Worker
from src.data.database_element import Person

class ConsumableStatusWorker(Worker):
    keywords = ["purchased", "missing"]
    
    def reply(self, message: str, sender_person: Person) -> str:
        """
        Update consumable status, reply with a message
        """

        # identify status
        message_list = message.split()
        status = None
        if "purchased" in message_list:
            if "missing" in message_list:
                return "Please only specify one status at a time, either 'purchased' or 'missing'"
            status = "purchased"
        elif "missing" in message_list:
            if "purchased" in message_list:
                return "Please only specify one status at a time, either 'purchased' or 'missing'"
            status = "missing"
        else:
            return "Please specify a status, either 'purchased' or 'missing'"
        message_list.remove(status)

        # identify consumable
        consumables = self.data.find('consumables', lambda consumable: consumable.name.lower() in message_list)
        if len(consumables) != 1:
            return f"Couldn't identify exactly one consumable with the given keywords {' '.join([w for w in message_list])}, please choose one consumable from that list: {', '.join([consumable.name for consumable in self.data.find(attribute_name='consumables')])}\n]"
        consumable = consumables[0]

        # identify responsible person
        responsible_persons = self.data.find('persons', lambda person: consumable.id in person.consumable_ids)
        if len(responsible_persons) != 1:
            found_responsible_persons_str = ',\n'.join([person.name for person in responsible_persons])
            return f"Couldn't identify exactly one person responsible for {consumable.name}, found the following responsible persons:\n[\n{found_responsible_persons_str}\n]"
        responsible_person = responsible_persons[0]

        # update status
        if status == "purchased":
            consumable.is_available = True
            if sender_person.id != responsible_person.id:
                return f"{sender_person.name} you are not responsible for {consumable.name}, its {responsible_person.name}'s responsibility. But thanks a lot for helping out!"
            return f"Thank you {sender_person.name} for purchasing {consumable.name}"

        elif status == "missing":
            consumable.is_available = False
            if sender_person.id == responsible_person.id:
                return f"Thank you for reporting! Buying {consumable.name} is on your list of responsibilities."
            if not responsible_person.is_present:
                return f"Thank you for reporting! The responsible person {responsible_person.name} is currently not present, so someone else needs to buy {consumable.name}."
            return f"Dear {responsible_person.name}, please buy {consumable.name}"
