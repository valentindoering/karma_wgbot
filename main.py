from src.data import Data
from src.utils import Config, CSVLogger, on_error_send_traceback
from src.openai import OpenAi
from src.telegram import Telegram, TelegramMessage
from src.wgbot import WgBot

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
        special_load_file="data/backup_data.json"
    )
    telegram = Telegram(
        bot_key = config.get('telegram')['bot_key'], 
        chat_id = config.get('telegram')['chat_id'],
        polling_interval_in_seconds=config.get('telegram')['polling_interval_in_seconds'],
    )
    wgbot = WgBot(
        data=data,
        ai=ai
    )

    keywords_trigger = [
            (["how to"], wgbot.how_to),
            (["info"], wgbot.info),
            (["karma"], wgbot.karma_transaction),
            (["done"], wgbot.task_done),
            (["present", "absent"], wgbot.presence_status),
            (["purchased", "missing"], wgbot.consumable_status),
            (["weekly rotation"], wgbot.weekly_rotation)
]

    @on_error_send_traceback(log_func=telegram.send)
    def reply(message: TelegramMessage):
        message.text = message.text.lower()
        for keywords, func in keywords_trigger:
            if any(keyword in message.text for keyword in keywords):
                return func(message)

    telegram.poll_reply(callback=reply)











    

    










