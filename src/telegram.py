import requests
import math
from urllib.parse import quote
import time


class TelegramMessage():
    def __init__(self, date, message_id, text, user_id):
        self.date = date
        self.message_id = message_id
        self.text = text
        self.user_id = user_id
    
    def __repr__(self):
        return f'TelegramMessage({self.date},{self.message_id},{self.text},{self.user_id})'

class Telegram():
    def __init__(self, bot_key: str, chat_id: str, polling_interval_in_seconds: int):
        self._bot_key = bot_key
        self._chat_id = chat_id
        self._polling_interval_in_seconds = polling_interval_in_seconds

        self._latest_message_id = None

    def _fetch(self, message: str) -> bool:
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

    def send(self, message: str) -> None:
        packages_remaining = [message]
        max_messages_num = 40
        while len(packages_remaining) > 0 and max_messages_num > 0:
            curr_package = packages_remaining.pop(0)
            message_sent = self._fetch(curr_package)
            if message_sent:
                max_messages_num -= 1
            if not message_sent:
                if len(curr_package) < 10:
                    self._fetch("Telegram failed")
                    break
                num_of_chars_first = math.ceil(len(curr_package) / 2)
                first_package = curr_package[0:num_of_chars_first]
                second_package = curr_package[num_of_chars_first : len(curr_package)]

                packages_remaining.insert(0, second_package)
                packages_remaining.insert(0, first_package)
        if max_messages_num == 0:
            self._fetch("Sending failed. Too many messages sent.")
    
    def _poll(self):
        url = (
            "https://api.telegram.org/bot"
            + self._bot_key
            + "/getUpdates"
        )
        response = requests.get(url).json()
        
        if response["ok"]:
            return response["result"]

        self._fetch("Poll failed")

    def latest_messages(self) -> "list[TelegramMessage]":
        response = self._poll()
        all_messages = [m["message"] for m in response if "message" in m]
        all_text_messages = [m for m in all_messages if "text" in m]
        chat_messages = [m for m in all_text_messages if int(m["chat"]["id"]) == int(self._chat_id)]
        latest_telegram_messages: list[TelegramMessage] = [TelegramMessage(date=m["date"], message_id=m["message_id"], text=m["text"], user_id=m["from"]["id"]) for m in chat_messages]
        latest_telegram_messages.sort(key=lambda m: m.date, reverse=True)
        return latest_telegram_messages
    
    def poll_reply(self, callback) -> None:
        """
        Polls for new messages each <polling_interval_in_seconds>. 
        If a new message is found, it calls the callback function with the new message as an argument.
        If the callback returns a string, it will be sent as a reply to the message.
        """
        while True:
            time.sleep(self._polling_interval_in_seconds)
            messages = self.latest_telegram_messages()

            if len(messages) == 0 or messages[0].message_id == self._latest_message_id:
                continue
            self._latest_message_id = messages[0].message_id
            
            reply = callback(messages[0])
            if reply:
                self.send(reply)
