from src.worker.worker import Worker
from src.data.database_element import Person

class PresenceStatusWorker(Worker):
    keywords = ["present", "absent"]

    def reply(self, message: str, sender_person: Person) -> str:
        """
        Update presence status, reply with a message
        """

        # identify status
        message_list = message.split()
        status = None
        if "present" in message_list:
            if "absent" in message_list:
                return "Please only specify one status at a time, either 'present' or 'absent'"
            status = "present"
        elif "absent" in message_list:
            if "present" in message_list:
                return "Please only specify one status at a time, either 'present' or 'absent'"
            status = "absent"
        else:
            return "Please specify a status, either 'present' or 'absent'"

        # update status
        if status == "present":
            sender_person.is_present = True

            # first home? get trash duty
            all_absent = all([not person.is_present for person in self.data.find('persons')])
            if all_absent:
                trash_task_id = self.data.find('tasks', lambda t: t.name == 'trash')[0].id
                person_with_trash_task = self.data.find('persons', lambda p: trash_task_id in p.current_task_ids)[0]
                person_with_trash_task.current_task_ids.remove(trash_task_id)
                sender_person.current_task_ids.append(trash_task_id)
                return f"Welcome back home {sender_person.name}! As the first one to return you get to start the trash duty."

            return f"Welcome back home {sender_person.name}!"

        elif status == "absent":
            sender_person.is_present = False
            trash_task_id = self.data.find('tasks', lambda t: t.name == 'trash')[0].id
            if trash_task_id in sender_person.current_task_ids:
                next_present_prson = self._next_present_person(sender_person)
                if next_present_prson:
                    sender_person.current_task_ids.remove(trash_task_id)
                    next_present_prson.current_task_ids.append(trash_task_id)
                    return f"Have a great trip, {sender_person.name}. {next_present_prson.name} will be responsible for the trash next trash as you are absent now."
            return f"Have a great trip, {sender_person.name}."
