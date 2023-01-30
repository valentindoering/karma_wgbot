import yaml
import os
import math
import requests
from urllib.parse import quote
import pprint
from src.data import Data
from src.utils import Config, CSVLogger, on_error_send_traceback
from src.openai import OpenAi
from src.telegram import Telegram


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
        chat_id = config.get('telegram')['chat_id']
    )

    print(telegram.latest_telegram_messages())










    

    










