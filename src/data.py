import json

class DatabaseElement():
    def __init__(self):
        self._observer_callbacks = []
    
    def register_observer_callback(self, callback):
        self._observer_callbacks.append(callback)

    def to_dict(self):
        tmp_dict = self.__dict__.copy()
        tmp_dict.pop("_observer_callbacks")
        return tmp_dict
    
    def __repr__(self) -> str:
        return str(self.to_dict())
    
    def __setattr__(self, __name: str, __value) -> None:
        val = super().__setattr__(__name, __value)
        if __name != "_observer_callbacks" and self._observer_callbacks:
            for callback in self._observer_callbacks:
                callback()
        return val


class Task(DatabaseElement):
    def __init__(self, id, name, is_done, is_weekly):
        super().__init__()
        self.id = id
        self.is_weekly = is_weekly
        self.name = name
        self.is_done = is_done

class Consumable(DatabaseElement):
    def __init__(self, id, name, is_available):
        super().__init__()
        self.id = id
        self.name = name
        self.is_available = is_available

class Person(DatabaseElement):
    def __init__(self, id, name, telegram_id, is_present, karma, consumable_ids, current_task_ids, weekly_task_history_ids):
        super().__init__()
        self.id: int = id
        self.name: str = name
        self.telegram_id: int = telegram_id
        self.is_present: bool = is_present
        self.karma: int = karma
        self.consumable_ids: list[int] = consumable_ids

        # current tasks
        self.current_task_ids: list[int] = current_task_ids

        # history
        # [Task("bathroom"), Task("kitchen"), Task("floor"), Task("trash"),  Task("airing"))]
        self.weekly_task_history_ids: list[int] = weekly_task_history_ids


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