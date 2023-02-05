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