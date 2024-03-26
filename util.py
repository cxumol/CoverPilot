import tiktoken

from urllib.parse import urlparse
import requests

import logging

def mylogger(name, format, level=logging.INFO):
    # Create a custom logger
    logger = logging.getLogger("custom_logger")
    logger.setLevel(level)
    # Configure the custom logger with the desired settings
    formatter = logging.Formatter(format)
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(formatter)
    # file_handler = logging.FileHandler('custom_logs.log')
    # file_handler.setFormatter(formatter)
    logger.addHandler(c_handler)

    return logger


def count_token(text, encoding="cl100k_base"):
    return len(tiktoken.get_encoding(encoding).encode(text))


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_valid_openai_api_key(api_base:str, api_key: str)->bool:
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(api_base, headers=headers)

    return response.status_code == 200


def zip_api(api_base:str, api_key:str, model:str)->dict[str, str]:
    return {"base": api_base, "key": api_key, "model": model}
