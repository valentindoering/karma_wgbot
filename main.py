from src.data.data import Data
from src.utils import Config, CSVLogger, on_error_send_traceback
from src.openai import OpenAi
from src.telegram import Telegram, TelegramMessage
from src.wgbot import Wgbot

if __name__ == "__main__":

    config = Config(
        config_file='config.yml'
    )
    log_in_csv = CSVLogger(
        file_name = config.get('environment_files')['log']
    ).log
    ai = OpenAi(
        organization = config.get('openai')['organization'], 
        api_key = config.get('openai')['api_key'], 
        model = config.get("openai")["model"], 
        max_tokens_per_request = config.get("openai")["max_tokens_per_request"],
        logger=log_in_csv
    )
    data = Data(
        data_file = config.get('environment_files')['data'], 
        # special_load_file="data/backup_data.json"
    )
    telegram = Telegram(
        bot_key = config.get('telegram')['bot_key'], 
        chat_id = config.get('telegram')['chat_id'],
        polling_interval_in_seconds=config.get('telegram')['polling_interval_in_seconds']
    )
    wgbot = Wgbot(data=data)

    def add_briefing_to_reply(sender_name: str, message: str, reply: str) -> str:
        # return f"""
        #     We are 3 students living together in one apartment. Whenever we do a task for the common household or buy something, are absent for the next time, are back, we write a message in our common chat.
        #     You are supposed to play the chatbot that replies to the messages in the chat. You should create a pleasant atmosphere in the chat with creative, funny or appreciative answers.

        #     {sender_name} has just sent the following message to the chat:
        #     '{message}'
            
        #     Please communicate the following answer in your own words:
        #     '{reply}'
        #     """
        return f"""
I want you to act as mom, that wants to encourage her kid {sender_name}. You are now in a conversation with your kid. It said '{message}'. I will now give you the answer on that question. Dont change the meaning of the answer, but say in your own words acting as the caring mom. You should reply: '{reply}'
        """

    @on_error_send_traceback(log_func=telegram.send)
    def reply(message: TelegramMessage) -> str:

        # identify sender
        sender_persons = data.find('persons', lambda person: person.telegram_id == message.user_id)
        if len(sender_persons) != 1:
            persons_found_str = ',\n'.join([person for person in sender_persons])
            return f"Coulnd't identify exactly one person with telegram id {message.user_id}, found:\n[\n{persons_found_str}\n]"
        sender_person = sender_persons[0]

        return ai.ask(
            add_briefing_to_reply(
                sender_name=sender_person.name,
                message=message.text,
                reply=wgbot.ask(message=message.text, sender_person=sender_person)
            )   
        )
        # return wgbot.ask(message=message.text, sender_person=sender_person)
    
    # Program Loop
    telegram.poll_reply(callback=reply)











    

    










