import tiktoken

from urllib.parse import urlparse
import requests
import logging

from icecream import ic

from typing import Generator


def mylogger(name, format, level=logging.INFO):
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Configure the custom logger with the desired settings
    formatter = logging.Formatter(format)
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(formatter)
    # file_handler = logging.FileHandler('custom_logs.log')
    # file_handler.setFormatter(formatter)
    logger.addHandler(c_handler)

    return logger


def count_token(text, encoding="cl100k_base") -> int:
    return len(tiktoken.get_encoding(encoding).encode(text))


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_valid_openai_api_key(api_base: str, api_key: str) -> bool:
    headers = {"Authorization": f"Bearer {api_key}"}
    test_url = f"{api_base}/models"
    response = requests.get(test_url, headers=headers)
    if response.status_code in range(200,300):
        ic(response.text())
    return response.status_code in range(200,300)


def checkAPI(api_base: str, api_key: str):
    if not is_valid_openai_api_key(api_base, api_key):
        raise ValueError(
            "API not available. Please double check your API settings. If you don't have any API key, try getting one from https://beta.openai.com/account/api-keys"
        )


def zip_api(api_base: str, api_key: str, model: str) -> dict[str, str]:
    return {"base": api_base, "key": api_key, "model": model}


def stream_together(*gens: Generator):
    ln = len(gens)
    result = [""] * ln  # Mind type here
    while 1:
        stop: bool = True
        for i in range(ln):
            try:
                n = next(gens[i])
                if "delta" in dir(n):
                    n = n.delta
                result[i] += n
                stop = False
            except StopIteration:
                # info(f"gen[{i}] exhausted")
                pass
        yield result
        if stop:
            break
