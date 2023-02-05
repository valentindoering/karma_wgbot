from src.worker.worker import Worker
from src.data.database_element import Person


class HowToWorker(Worker):
    keywords = ["how_to"]

    def reply(self, message: str, person: Person) -> str:
        """
        Reply with a message on how to use the bot
        """

        return f"""Commands, that the Kiefer Karma Bot understands:
        - 'how_to': Get THIS message, about how to use the bot
        - 'info': Get information about the current state of the bots database
        - 'karma': Transfer your karma points to people, eg.: 'Paula 5 karma' | <{", ".join([f"({person.name})" for person in self.data.find('persons')])}> <amount> karma
        - 'done': Mark a task as done, eg.: 'bathroom done' | <{", ".join([f"({task.name})" for task in self.data.find('tasks')])}> done'
        - 'present' / 'absent': Update your presence status, eg.: 'absent'
        - 'purchased' / 'missing': Update the status of a consumable, eg.: 'purchased toilet paper'| <missing / purchased> <{", ".join([f"({consumable.name})" for consumable in self.data.find('consumables')])}>
        - 'weekly_rotation': Get weekly report about completed tasks, rotate weekly tasks
        """