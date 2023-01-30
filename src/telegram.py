import requests
import math
from urllib.parse import quote


class TelegramMessage():
    def __init__(self, date, message_id, text, user_id):
        self.date = date
        self.message_id = message_id
        self.text = text
        self.user_id = user_id
    
    def __repr__(self):
        return f'TelegramMessage({self.date},{self.message_id},{self.text},{self.user_id})'

class Telegram():
    def __init__(self, bot_key: str, chat_id: str):
        self._bot_key = bot_key
        self._chat_id = chat_id

    def _telegram_fetch(self, message: str) -> bool:
        message = str(message)

        # updates and chatId https://api.telegram.org/bot<YourBOTToken>/getUpdates
        # For \n use %0A message = message.replace(/\n/g, "%0A")
        url = (
            "https://api.telegram.org/bot"
            + self._bot_key
            + "/sendMessage?chat_id="
            + self._chat_id
            + "&text="
            + quote(message)
        )

        try:
            response = (requests.get(url)).json()
            return response["ok"]
        except:
            return False

    def send_telegram(self, message: str) -> None:
        packages_remaining = [message]
        max_messages_num = 40
        while len(packages_remaining) > 0 and max_messages_num > 0:
            curr_package = packages_remaining.pop(0)
            message_sent = self._telegram_fetch(curr_package)
            if message_sent:
                max_messages_num -= 1
            if not message_sent:
                if len(curr_package) < 10:
                    self._telegram_fetch("Telegram failed")
                    break
                num_of_chars_first = math.ceil(len(curr_package) / 2)
                first_package = curr_package[0:num_of_chars_first]
                second_package = curr_package[num_of_chars_first : len(curr_package)]

                packages_remaining.insert(0, second_package)
                packages_remaining.insert(0, first_package)
        if max_messages_num == 0:
            self._telegram_fetch("Sending failed. Too many messages sent.")
    
    def _poll_telegram(self):
        url = (
            "https://api.telegram.org/bot"
            + self._bot_key
            + "/getUpdates"
        )
        response = requests.get(url).json()
        
        if response["ok"]:
            return response["result"]

        self._telegram_fetch("Poll failed")

    def latest_telegram_messages(self) -> "list[TelegramMessage]":
        response = self._poll_telegram()
        all_messages = [m["message"] for m in response if "message" in m]
        all_text_messages = [m for m in all_messages if "text" in m]
        chat_messages = [m for m in all_text_messages if int(m["chat"]["id"]) == int(self._chat_id)]
        latest_telegram_messages: list[TelegramMessage] = [TelegramMessage(date=m["date"], message_id=m["message_id"], text=m["text"], user_id=m["from"]["id"]) for m in chat_messages]
        latest_telegram_messages.sort(key=lambda m: m.date, reverse=True)
        return latest_telegram_messages