import json
from src.data.database_element import Person, Consumable, Task

class Data():

    def __init__(self, data_file: str, special_load_file: str = None):
        self._data_file = data_file

        persons, consumables, tasks = self._load_data(special_load_file=special_load_file)
        for data_list in [persons, consumables, tasks]:
            for element in data_list:
                element.register_observer_callback(self.save_data)
            
        self.persons: list[Person] = persons
        self.consumables: list[Consumable] = consumables
        self.tasks: list[Task] = tasks
    
    def find(self, attribute_name: str, find_func=lambda x: x):
        return list(filter(find_func, self.__getattribute__(attribute_name)))

    
    def _load_data(self, special_load_file: str = None):
        load_file = special_load_file if special_load_file else self._data_file
        with open(load_file, 'r') as f:
            data = json.load(f)
        
        persons: list[Person] = []
        for person in data['persons']:
            persons.append(
                Person(
                    id = person["id"], 
                    name = person["name"], 
                    telegram_id = person["telegram_id"],
                    is_present = person["is_present"], 
                    karma = person["karma"], 
                    consumable_ids = person["consumable_ids"], 
                    current_task_ids = person["current_task_ids"], 
                    weekly_task_history_ids = person["weekly_task_history_ids"]
                )
            )
        
        consumables: list[Consumable] = []
        for consumable in data['consumables']:
            consumables.append(
                Consumable(
                    id = consumable["id"], 
                    name = consumable["name"], 
                    is_available = consumable["is_available"]
                )
            )

        tasks: list[Task] = []
        for task in data['tasks']:
            tasks.append(
                Task(
                    id = task["id"], 
                    name = task["name"], 
                    is_done = task["is_done"], 
                    is_weekly = task["is_weekly"]
                )
            )
        
        return persons, consumables, tasks

    def save_data(self):
        print("Saving data...")
        with open(self._data_file, 'w') as f:
            data = {
                "persons": [person.to_dict() for person in self.persons],
                "consumables": [consumable.to_dict() for consumable in self.consumables],
                "tasks": [task.to_dict() for task in self.tasks]
            }
            json.dump(data, f, indent=1)