from src.data import Data, Person
from src.openai import OpenAi
from src.telegram import TelegramMessage

class Wgbot():
    def __init__(self, data: Data, ai: OpenAi):
        self.data = data
        self.ai = ai
    
    def _get_sender_person(self, message: TelegramMessage) -> tuple(str, Person):
        # find data entry of sender
        sender_persons = self.data.find('persons', lambda person: person.telegram_id == message.user_id)
        if len(sender_persons) != 1:
            return f"Coulnd't identify exactly one person with telegram id {message.user_id}, found:\n[\n{',\n'.join([person for person in sender_persons])}\n]", None
        return None, sender_persons[0]

    def _get_task(self, message: TelegramMessage) -> tuple(str, Person):
        # find data entry of task
        message_list = message.split()
        message_list.remove("done")
        if len(message_list) == 0:
            return "Please also specify the task you want to mark as done, e.g. 'kitchen done'", None
        tasks = self.data.find(attribute_name="tasks", find_func=lambda x: x.name in message_list)
        if len(tasks) != 1:
            return f"Couldn't identify exactly one task with the given keywords {' '.join([w for w in message_list])}, please choose one of the following keywords: {', '.join([task.name for task in self.data.find(attribute_name='tasks')])}\n]", None
        return None, tasks[0]

    def _next_present_person(self, current_person: Person) -> Person:
        persons = self.data.find('persons')
        for i in range(1, len(persons)):
            new_assignee_id = persons[(current_person.id + i) % len(persons)]
            person = self.data.find('persons', lambda p: p.id == new_assignee_id)
            if person.is_present:
                return person
        return None

    def _weekly_report_person(self, person: Person) -> Person:
        completed_tasks = [self.data.find('tasks', lambda t: t.id == t_id)[0] for t_id in person.weekly_task_history_ids]
        completed_tasks_count = []
        for unique_completed_task in set(completed_tasks):
            completed_tasks_count = (unique_completed_task, completed_tasks.count(unique_completed_task))
        print_completed_task = lambda task, count: f"{task.name} ({count}x)" if count > 1 else f"{task.name}"

        if len(completed_tasks_count) == 0 and not person.is_present:
            return f"{person.name} is absent"
        return f"{person.name}: {', '.join([print_completed_task(task, count) for task, count in completed_tasks_count])}"

    def _weekly_tasks_person(self, person: Person) -> Person:
        current_tasks = [self.data.find('tasks', lambda t: t.id == t_id)[0] for t_id in person.current_task_ids]
        if not person.is_present:
            return f"{person.name} is absent"
        return f"{person.name}: {', '.join([task.name for task in current_tasks])}"

    
    # keyword functions -----------------------------------------------------------------------------------------------
    
    def task_done(self, message: TelegramMessage) -> str:
        """
        Mark a task as done, reply with a message
        """
        error, sender_person = self._get_sender_person(message)
        if error: return error

        error, task = self._get_task(message)
        if error: return error

        # task cases ------------------------------------
        if task.name == "airing" or task.name == "peter":
            sender_person.weekly_task_history_ids.append(task.id)
            return self.ai.ask(f"Please come up with a creative message to thank {sender_person.name} for airing the apartment")

        elif task.name == "trash":
            sender_person.weekly_task_history_ids.append(task.id)
            if task.id not in sender_person.current_task_ids:
                person_assigned = [person for person in self.data.find('persons') if task.id in person.current_task_ids][0]
                if len(person_assigned) != 1:
                    return f"Couldn't identify exactly one person assigned to bringing down the trash, found:\n[\n{',\n'.join([person for person in person_assigned])}\n]"
                return f"{sender_person.name} you are currently not assigned to bring down the trash, its {person_assigned.name}'s turn this week. But thanks a lot for helping out!"
            task.is_done = False

            next_present_prson = self._next_present_person(sender_person)
            if next_present_prson:
                sender_person.current_task_ids.remove(task.id)
                next_present_prson.current_task_ids.append(task.id)
                return self.ai.ask(f"Please come up with a creative message to thank {sender_person.name} for bringing down the trash. At the same time inform, that the next trash is the responsibility of {next_present_prson.name}.")
            return self.ai.ask(f"Please come up with a creative message to thank {sender_person.name} for bringing down the trash. At the same time inform, that as all other people are 'absent', thats why the trash remains this persons task")

        else:
            if task.name not in ["kitchen", "bathroom", "floor"]:
                return f"Sorry, task '{task.name}' is not supported yet. Please choose one of the following keywords: {', '.join([task.name for task in self.data.find(attribute_name='tasks')])}\n]"

            sender_person.weekly_task_history_ids.append(task.id)
            if task.id not in sender_person.current_task_ids:
                person_assigned = [person for person in self.data.find('persons') if task.id in person.current_task_ids][0]
                if len(person_assigned) != 1:
                    return f"Couldn't identify exactly one person assigned to {task.name}, found:\n[\n{',\n'.join([person for person in person_assigned])}\n]"
                return f"{sender_person.name} you are currently not assigned to do the {task.name}, its {person_assigned.name}'s turn this week. But thanks a lot for helping out!"
            task.is_done = True
            return self.ai.ask(f"Please come up with a creative message to thank {sender_person.name} for doing the {task.name}")

    def karma_transaction(self, message: TelegramMessage) -> str:
        """
        Transfer karma between persons, reply with a message
        """

        # identify sender
        sender_person = self._get_sender_person(message)
        if isinstance(sender_person, str): return sender_person

        # identify receiver
        message_list = message.split()
        message_list.remove("karma")
        if len(message_list) == 0:
            return "For a karma transaction please also specify the name of the receiver and the amount e.g.: 'Paula 5 karma'"
        receiver_persons = self.data.find('persons', lambda person: person.name.lower() in message_list)
        if len(receiver_persons) != 1:
            return f"Couldn't identify exactly one person with the given keywords {' '.join([w for w in message_list])}, please choose one person from that list: {', '.join([person.name for person in self.data.find(attribute_name='persons')])}\n]"
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
        confirmation_message = f"Transaction of {amount} karma from {sender_person.name} to {receiver_person.name} successful. New karma balance:\n{', '.join([f'{person.name}: {person.karma}' for person in self.data.find('persons')])}"
        return self.ai.ask(f"Plese come up with a creative version of the following message:\n{confirmation_message}")

    def consumable_status(self, message: TelegramMessage) -> str:
        """
        Update consumable status, reply with a message
        """

        # identify sender
        sender_person = self._get_sender_person(message)
        if isinstance(sender_person, str): return sender_person

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
        responsible_persons = self.data.find('persons', lambda person: consumable.id in person.current_consumable_ids)
        if len(responsible_persons) != 1:
            return f"Couldn't identify exactly one person responsible for {consumable.name}, found the following responsible persons:\n[\n{',\n'.join([person.name for person in responsible_persons])}\n]"
        responsible_person = responsible_persons[0]

        # update status
        if status == "purchased":
            consumable.is_available = True
            if sender_person.id != responsible_person.id:
                return f"{sender_person.name} you are not responsible for {consumable.name}, its {responsible_person.name}'s responsibility. But thanks a lot for helping out!"
            return self.ai.ask(f"Please come up with a creative message to thank {sender_person.name} for purchasing the {consumable.name}")

        elif status == "missing":
            consumable.is_available = False
            if sender_person.id == responsible_person.id:
                return f"Thank you for reporting! Buying {consumable.name} is on your list of responsibilities."
            if not responsible_person.is_present:
                return f"Thank you for reporting! The responsible person {responsible_person.name} is currently not present, so someone else needs to buy {consumable.name}."
            return self.ai.ask(f"Please come up with a kind message that asks {responsible_person.name} to buy {consumable.name}")

    def presence_status(self, message: TelegramMessage) -> str:
        """
        Update presence status, reply with a message
        """

        # identify sender
        error, sender_person = self._get_sender_person(message)
        if error: return error

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
            all_absent = all([not person.is_present for person in self.data.find('persons')])
            sender_person.is_present = True
            if all_absent:
                trash_task_id = self.data.find('tasks', lambda t: t.name == 'trash')[0].id
                person_with_trash_task = self.data.find('persons', lambda p: trash_task_id in p.current_task_ids)[0]
                person_with_trash_task.current_task_ids.remove(trash_task_id)
                sender_person.current_task_ids.append(trash_task_id)
                return self.ai.ask(f"{sender_person.name} is back in the apartment after some time. Please come up with a creative message to welcome {sender_person.name} back. At the same time inform, that as the first person back, {sender_person.name} is responsible for the next trash.")
            return self.ai.ask(f"{sender_person.name} is back in the apartment after some time. Please come up with a creative message to welcome {sender_person.name} back.")

        elif status == "absent":
            sender_person.is_present = False
            trash_task_id = self.data.find('tasks', lambda t: t.name == 'trash')[0].id
            if trash_task_id in sender_person.current_task_ids:
                next_present_prson = self._next_present_person(sender_person)
                if next_present_prson:
                    sender_person.current_task_ids.remove(trash_task_id)
                    next_present_prson.current_task_ids.append(trash_task_id)
                    return self.ai.ask(f"{sender_person.name} is about to leave the apartment for some time, please write a creative message wishing a good time. At the same time inform, that as {sender_person.name} is now absent the next trash is the responsibility of {next_present_prson.name}.")
            return self.ai.ask(f"{sender_person.name} is about to leave the apartment for some time, please write a creative message wishing a good time")

    def how_to(self, _: TelegramMessage) -> str:
        """
        Reply with a message on how to use the bot
        """

        return f"""Commands, that the Kiefer Karma Bot understands:
        - 'how to': Get THIS message, about how to use the bot
        - 'info': Get information about the current state of the bots database
        - 'karma': Transfer your karma points to people, eg.: 'Paula 5 karma' | <{", ".join([f"({person.name})" for person in self.data.find('persons')])}> <amount> karma
        - 'done': Mark a task as done, eg.: 'bathroom done' | <{", ".join([f"({task.name})" for task in self.data.find('tasks')])}> done'
        - 'present' / 'absent': Update your presence status, eg.: 'absent'
        - 'purchased' / 'missing': Update the status of a consumable, eg.: 'purchased toilet paper'| <missing / purchased> <{", ".join([f"({consumable.name})" for consumable in self.data.find('consumables')])}>
        - 'weekly rotation': Get weekly report about completed tasks, rotate weekly tasks
        """

    def info(self, _: TelegramMessage) -> str:
        """
        Reply with a message on the current state of the bots database
        """

        return f"""The current state of the bots database is:
        - {len(self.data.find('persons'))} persons: \n\t{', \n\t'.join([person for person in self.data.find('persons')])}
        - {len(self.data.find('tasks'))} tasks: \n\t{', \n\t'.join([task for task in self.data.find('tasks')])}
        - {len(self.data.find('consumables'))} consumables: \n\t{', \n\t'.join([consumable for consumable in self.data.find('consumables')])}
        """

    def weekly_rotation(self, _: TelegramMessage) -> str:
        """
        Get weekly report about completed tasks, rotate weekly tasks
        Idea: before deleting the history, a snapshot of the history could be saved in a separate file
        """

        # write weekly report
        weekly_task_history_per_person = [self._weekly_report_person(person) for person in self.data.find('persons')]
        weekly_report = f"*Weekly report*\nThank you for doing these tasks!\n{'\n'.join(weekly_task_history_per_person)}"

        # rotate weekly tasks
        persons = self.data.find('persons')
        task_assignments = []
        for person in persons:
            current_weekly_tasks = [task for task in self.data.find('tasks') if task.id in person.current_task_ids and task.is_weekly]
            for task in current_weekly_tasks:
                person.current_task_ids.remove(task.id)
            next_person = self.data.find('persons', lambda person: person.id + 1 % len(persons))
            task_assignments.append((next_person, current_weekly_tasks))
        for person, tasks in task_assignments:
            for task in tasks:
                person.current_task_ids.append(task.id)

        # reset weekly task history
        for person in persons:
            person.weekly_task_history = []
        
        # inform about new weekly tasks
        weekly_tasks_per_person = [self._weekly_tasks_person(person) for person in self.data.find('persons')]
        new_weekly_tasks = f"*Task for this week*\n{'\n'.join(weekly_tasks_per_person)}"

        return f"{weekly_report}\n\n{new_weekly_tasks}"
