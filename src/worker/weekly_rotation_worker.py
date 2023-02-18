from src.data.database_element import Person
from src.worker.worker import Worker

class WeeklyRotationWorker(Worker):
    keywords = ["weekly_rotation"]

    def _weekly_report_person(self, person: Person) -> Person:
        completed_tasks = [self.data.find('tasks', lambda t: t.id == t_id)[0] for t_id in person.weekly_task_history_ids]
        completed_tasks_count = []
        for unique_completed_task in set(completed_tasks):
            completed_tasks_count.append((unique_completed_task, completed_tasks.count(unique_completed_task)))
        print_completed_task = lambda task, count: f"{task.name} ({count}x)" if count > 1 else f"{task.name}"

        if len(completed_tasks_count) == 0 and not person.is_present:
            return f"{person.name} is absent"
        return f"{person.name}: {', '.join([print_completed_task(task, count) for task, count in completed_tasks_count])}"

    def _weekly_tasks_person(self, person: Person) -> Person:
        current_tasks = [self.data.find('tasks', lambda t: t.id == t_id)[0] for t_id in person.current_task_ids]
        if not person.is_present:
            return f"{person.name} is absent"
        return f"{person.name}: {', '.join([task.name for task in current_tasks])}"
    
    # Public -----------------------------------------------------------------

    def reply(self, message: str, sender_person: Person) -> str:
        """
        Get weekly report about completed tasks, rotate weekly tasks
        Idea: before deleting the history, a snapshot of the history could be saved in a separate file
        """

        # write weekly report
        weekly_task_history_per_person_str = '\n'.join([self._weekly_report_person(person) for person in self.data.find('persons')])
        weekly_report = f"---------- Weekly report ----------\n\nThank you for doing these tasks!\n{weekly_task_history_per_person_str}"

        # rotate weekly tasks
        # give my tasks to the person with the next id
        persons = self.data.find('persons')
        task_assignments = []
        for person in persons:
            current_weekly_tasks = [task for task in self.data.find('tasks') if task.id in person.current_task_ids and task.is_weekly]
            for task in current_weekly_tasks:
                person.current_task_ids.remove(task.id)
            next_persons = self.data.find('persons', lambda p: p.id == (person.id + 1) % len(persons))
            if len(next_persons) != 1:
                return "Error: next person not found"
            next_person = next_persons[0]
            task_assignments += [(next_person, current_weekly_tasks)]
        for person, tasks in task_assignments:
            for task in tasks:
                person.current_task_ids += [task.id]

        # reset weekly task history
        for person in persons:
            person.weekly_task_history_ids = []
        
        # inform about new weekly tasks
        weekly_tasks_per_person_str = '\n'.join([self._weekly_tasks_person(person) for person in self.data.find('persons')])
        new_weekly_tasks = f"New tasks for this week ----------\n\n{weekly_tasks_per_person_str}"

        # karma info
        karma_txt = '\n'.join([f'{person.name}: {person.karma}' for person in self.data.find('persons')])
        karma_info = f"Karma info ----------\n\n{karma_txt}"

        return f"{weekly_report}\n\n{new_weekly_tasks}\n\n{karma_info}"