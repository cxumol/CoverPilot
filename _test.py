from taskAI import TaskAI
from taskNonAI import compile_pdf
from _data_test import mock_jd, mock_cv, pdf_context
from _secret import api_test

from llama_index.llms.openai_like import OpenAILike
from llama_index.core.llms import ChatMessage


def test_ai_integration():
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant"),
        ChatMessage(role="user", content="What is your name"),
    ]
    print("Testing integration:")
    response = OpenAILike(
        model=api_test["model"],
        api_key=api_test["key"],
        api_base=api_test["base"],
        max_retries=0,
        is_chat_model=True,
    ).chat(messages)
    print(response)

def test_taskAI():
    taskAI = TaskAI(api_test)
    gen = taskAI.cv_preprocess(mock_cv)
    for chunk in gen:
        print(chunk)

def test_typst_pdf():
    compile_pdf(tmpl_path='typst/template_letter.tmpl', context=pdf_context, output_path='test_result.pdf')
    # os

if __name__ == "__main__":
    # test_taskAI()
    # test_ai_integration()
    test_typst_pdf()