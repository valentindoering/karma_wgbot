from src.worker.worker import Worker
from src.data.database_element import Person

class InfoWorker(Worker):
    keywords = ["info"]

    def reply(self, message: str, person: Person) -> str:
        """
        Reply with a message on the current state of the bots database
        """
        tab_space = '      '
        persons_info_str = f', \n{tab_space}'.join([str(person) for person in self.data.find('persons')])
        tasks_info_str = f', \n{tab_space}'.join([str(task) for task in self.data.find('tasks')])
        consumables_info_str = f', \n{tab_space}'.join([str(consumable) for consumable in self.data.find('consumables')])

        return f"""The current state of the bots database is:
- {len(self.data.find('persons'))} persons: \n{tab_space}{persons_info_str}
- {len(self.data.find('tasks'))} tasks: \n{tab_space}{tasks_info_str}
- {len(self.data.find('consumables'))} consumables: \n{tab_space}{consumables_info_str}
        """
