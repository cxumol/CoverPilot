from llama_index.llms.openai_like import OpenAILike
from llama_index.core.llms import ChatMessage  # , MessageRole
from llama_index.core import ChatPromptTemplate

from util import mylogger

logger = mylogger(__name__,'%(asctime)s:%(levelname)s:%(message)s')
info = logger.info


## define templates

### topic,input
JD_PREPROCESS = ChatPromptTemplate(
    [
        ChatMessage(
            role="system",
            content="You are a content extractor. You never paraphrase; you only reduce content at the sentence level. Your mission is to extract information directly related to {topic} from user input. Make sure output contains complete information.",
        ),
        ChatMessage(role="user", content="{input}"),
    ]
)

### input
CV_PREPROCESS = ChatPromptTemplate(
    [
        ChatMessage(
            role="system",
            content="You are an AI text converter alternative to pandoc. Your mission is to convert the input content into markdown. Regarding styles, only keep headers, lists and links, and remove other styles.",
        ),
        ChatMessage(role="user", content="{input}"),
    ]
)

## basic func


def oai(base: str, key: str, model: str, **kwargs) -> OpenAILike:
    return OpenAILike(
        api_base=base,
        api_key=key,
        model=model,
        is_chat_model=True,
        context_window=window_size,
        **kwargs,
    )


## tasks
class TaskAI(OpenAILike):
    def __init__(self, api: dict[str, str], **kwargs):
        def guess_window_size(model=api["model"]):
            _mid = model.lower()
            windows: dict = {
                8000: ["gemma", "8k"],
                16000: ["16k"],
                32000: ["mistral", "mixtral", "32k"],
            }
            window_size = 3900
            for ws, names in windows.items():
                if any([n in _mid for n in names]):
                    window_size = ws
            info(f"use context window size: {window_size} for {model}")
            return window_size

        super().__init__(
            api_base=api["base"], api_key=api["key"], model=api["model"], is_chat_model=True, context_window=guess_window_size(), **kwargs
        )

    def jd_preprocess(self, topic: str, input: str):
        return self.stream_chat(JD_PREPROCESS.format_messages(topic=topic, input=input))

    def cv_preprocess(self, input: str):
        return self.stream_chat(CV_PREPROCESS.format_messages(input=input))
