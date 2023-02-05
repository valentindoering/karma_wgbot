from src.data.database_element import Person
from src.worker.worker import Worker

class TaskDoneWorker(Worker):
    keywords = ["done"]

    def _get_task(self, message: str) -> "tuple[str, Person]":
        # find data entry of task
        message_list = message.split()
        message_list.remove("done")
        if len(message_list) == 0:
            return "Please also specify the task you want to mark as done, e.g. 'kitchen done'", None
        tasks = self.data.find(attribute_name="tasks", find_func=lambda x: x.name in message_list)
        if len(tasks) != 1:
            return f"Couldn't identify exactly one task with the given keywords {' '.join([w for w in message_list])}, please choose one of the following keywords: {', '.join([task.name for task in self.data.find(attribute_name='tasks')])}\n]", None
        return None, tasks[0]

    # Public --------------------------------------------------------------
    
    def reply(self, message: str, sender_person: Person) -> str:
        """
        Mark a task as done, reply with a message
        """

        error, task = self._get_task(message)
        if error: return error

        # task cases ------------------------------------
        if task.name == "airing" or task.name == "peter":
            sender_person.weekly_task_history_ids.append(task.id)
            return f"Thank you {sender_person.name} for airing the apartment"

        elif task.name == "trash":
            sender_person.weekly_task_history_ids.append(task.id)
            if task.id not in sender_person.current_task_ids:
                person_assigned = [person for person in self.data.find('persons') if task.id in person.current_task_ids][0]
                if len(person_assigned) != 1:
                    persons_assigned_str = ',\n'.join([person for person in person_assigned])
                    return f"Couldn't identify exactly one person assigned to bringing down the trash, found:\n[\n{persons_assigned_str}\n]"
                return f"{sender_person.name} you are currently not assigned to bring down the trash, its {person_assigned.name}'s turn this week. But thanks a lot for helping out!"
            task.is_done = False

            next_present_prson = self._next_present_person(sender_person)
            if next_present_prson:
                sender_person.current_task_ids.remove(task.id)
                next_present_prson.current_task_ids.append(task.id)
                return f"Thank you {sender_person.name} for bringing down the trash. {next_present_prson.name} will be responsible for the next trash."
            return f"Thank you {sender_person.name} for bringing down the trash. As all other people are 'absent', the trash remains your task"

        else:
            if task.name not in ["kitchen", "bathroom", "floor"]:
                return f"Sorry, task '{task.name}' is not supported yet. Please choose one of the following keywords: {', '.join([task.name for task in self.data.find(attribute_name='tasks')])}\n]"

            sender_person.weekly_task_history_ids.append(task.id)
            if task.id not in sender_person.current_task_ids:
                person_assigned = [person for person in self.data.find('persons') if task.id in person.current_task_ids][0]
                if len(person_assigned) != 1:
                    persons_assigned_str = ',\n'.join([person for person in person_assigned])
                    return f"Couldn't identify exactly one person assigned to {task.name}, found:\n[\n{persons_assigned_str}\n]"
                return f"{sender_person.name} you are currently not assigned to do the {task.name}, its {person_assigned.name}'s turn this week. But thanks a lot for helping out!"
            task.is_done = True
            return f"Thank you {sender_person.name} for doing the {task.name}"