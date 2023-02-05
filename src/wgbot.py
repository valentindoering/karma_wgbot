from src.data.data import Data
from src.openai import OpenAi
from src.data.database_element import Person
from src.worker.info_worker import InfoWorker
from src.worker.how_to_worker import HowToWorker
from src.worker.karma_transaction_worker import KarmaTransactionWorker
from src.worker.presence_status_worker import PresenceStatusWorker
from src.worker.consumable_status_worker import ConsumableStatusWorker
from src.worker.weekly_rotation_worker import WeeklyRotationWorker
from src.worker.task_done_worker import TaskDoneWorker


class Wgbot():
    def __init__(self, data: Data):
        self.data = data
        worker_cls = [
            InfoWorker,
            HowToWorker,
            KarmaTransactionWorker,
            PresenceStatusWorker,
            ConsumableStatusWorker,
            WeeklyRotationWorker,
            TaskDoneWorker,
        ]
        self.workers = [cls(data=data) for cls in worker_cls]
    
    def _get_all_keywords(self) -> "list[str]":
        keywords = []
        for worker in self.workers:
            keywords +=worker.keywords
        return keywords

    # Public -------------------------------------------------------------------

    def ask(self, message: str, sender_person: Person) -> str:
        message = message.lower()

        # keyword triggered? else skip
        n_triggered = 0
        for worker in self.workers:
            if worker.is_triggered(message):
                n_triggered += 1
        if n_triggered == 0:
            return None

        # only one keyword triggered? else skip
        if n_triggered != 1:
            return f"I dont really get what you want, because you used multiple keywords. Please use exactly one keyword of the following: {', '.join(self._get_all_keywords())}."

        # answer
        for worker in self.workers:
            if worker.is_triggered(message):
                return worker.reply(message, sender_person)