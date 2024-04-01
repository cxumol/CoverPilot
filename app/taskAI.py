import json

from llama_index.llms.openai_like import OpenAILike
from llama_index.core.llms import ChatMessage  # , MessageRole
from llama_index.core import ChatPromptTemplate

from util import mylogger
from util import checkAPI

from icecream import ic

logger = mylogger(__name__, "%(asctime)s:%(filename)s:%(levelname)s:%(message)s")
## define templates

### topic,input
EXTRACT_INFO = ChatPromptTemplate(
    [
        ChatMessage(
            role="system",
            content="You are a content extractor. You never paraphrase; you only reduce content at the sentence level. Your mission is to extract {to_extract} from user input. Reformat the extraction in a clean style if extraction looks messey.",
        ),
        ChatMessage(role="user", content="{input}"),
    ]
)

### input
SIMPLIFY_MD = ChatPromptTemplate(
    [
        ChatMessage(
            role="system",
            content="You are an AI text converter alternative to pandoc. Your mission is to convert the input content into markdown. Regarding styles, only keep headers, lists and links, and remove other styles.",
        ),
        ChatMessage(role="user", content="{input}"),
    ]
)

### template, content
JSON_API = ChatPromptTemplate(
    [
        ChatMessage(
            role="system",
            content="You are a JSON API. Your mission is to convert user input into a valid and complete JSON object STRICTLY in this template: {template}. The output should be completely a plain json without nested structure. Never summerize, paraphrase or do anything else, just extract the information from the input and fill in the template.",
        ),
        ChatMessage(role="user", content="{content}"),
    ]
)
keys_to_template = lambda keys: json.dumps(dict().fromkeys(keys, ""))

### resume, jd
LETTER_COMPOSE = ChatPromptTemplate(
    [
        ChatMessage(
            role="system",
            content="""You are a thoughtful wordsmith. You have a deep understanding of the scoiety and the bussiness world. You are always willing to help people find a job. Your mission is to write a compelling cover letter tailored for user to get the specified job, based on the provided RESUME and JOB_DESCRIPTION. Your writing is based on ground truth and you never fabricate anything you are unsure about.

Before officially write the letter, think step by step. First, list what makes a perfect cover letter in general, and in order to write a perfect cover letter, what key points do you have to learn from the RESUME and JOB_DESCRIPTION. Then, carefully analyze the given RESUME and JOB_DESCRIPTION, take a deep breath and propose 3 best tactics to convince recruiter believe the applicant fit for the role. Ensure your thoughts are express clearly and then write the complete cover letter.""",
        ),
        ChatMessage(
            role="user",
            content="<RESUME>\n{resume}\n</RESUME>\n\n<JOB_DESCRIPTION>\n{jd}</JOB_DESCRIPTION>\n<ANALYSIS_REPORT>",
        ),
    ]
)

## basic func


## tasks
class TaskAI(OpenAILike):
    is_debug = False

    def __init__(self, api: dict[str, str], is_debug=False, **kwargs):
        log = logger.info

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
            log(f"use context window size: {window_size} for {model}")
            return window_size

        checkAPI(api_base=api["base"], api_key=api["key"])

        super().__init__(
            api_base=api["base"],
            api_key=api["key"],
            model=api["model"],
            is_chat_model=True,
            context_window=guess_window_size(),
            **kwargs,
        )
        self.is_debug = is_debug

    def _debug_print_msg(self, msg):
        if not self.is_debug:
            return
        for m in msg:
            print(m.content)

    def jd_preprocess(self, input: str):
        msg = EXTRACT_INFO.format_messages(
            to_extract="the job description part", input=input
        )

        return self.stream_chat(msg)

    def cv_preprocess(self, input: str):
        msg = SIMPLIFY_MD.format_messages(input=input)
        # if self.is_debug: logger.info(msg)
        return self.stream_chat(msg)

    def compose_letter_CoT(self, resume: str, jd: str):
        msg = LETTER_COMPOSE.format_messages(resume=resume, jd=jd)
        self._debug_print_msg(msg)
        return self.stream_chat(msg)

    def get_jobapp_meta(self, JD, CV):
        meta_JD = self.chat(
            JSON_API.format_messages(
                template=keys_to_template(["companyFullName", "jobTitle"]), content=JD
            )
        ).message.content
        # yield meta_JD
        meta_CV = self.chat(
            JSON_API.format_messages(
                template=keys_to_template(
                    ["applicantFullName", "applicantContactInformation"]
                ),
                content=CV,
            )
        ).message.content
        # yield meta_JD+'\n'+meta_CV
        try:
            meta_JD = json.loads(meta_JD.strip())
            meta_CV = json.loads(meta_CV.strip())
        except Exception as e:
            ic(e)
            raise ValueError(
                f"AI didn't return a valid JSON string. Try again or consider a better model for CheapAI. \n{meta_JD}\n{meta_CV}"
            )
        meta = dict()
        meta.update(meta_JD)
        meta.update(meta_CV)
        yield json.dumps(meta, indent=2)

    def purify_letter(self, full_text):
        return self.stream_chat(
            EXTRACT_INFO.format_messages(
                to_extract="the cover letter section starting from 'Dear Hiring Manager' or similar to 'Sincerely,' or similar",
                input=full_text,
            )
        )
