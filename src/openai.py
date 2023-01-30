import openai

class OpenAi():
    def __init__(self, organization: str, api_key: str, model: str, max_tokens_per_request: int, logger = print):
        openai.organization = organization
        openai.api_key = api_key

        self._model = model
        self._max_tokens_per_request = max_tokens_per_request

        self._logger = logger
    
    def ask(self, question):
        try:
            answer = openai.Completion.create(
                model=self._model,
                prompt=question,
                max_tokens=int(self._max_tokens_per_request),
                temperature=0
            )
            text = answer['choices'][0]['text']
            # new line in csv file with date, time, question, answer
            log_text = text.replace('\n', ' ')
            self._logger(f'{question},{log_text}')
            return text
        except Exception as err:
            self._logger(f'{question},{"ChatGPT failed"}')
            raise err