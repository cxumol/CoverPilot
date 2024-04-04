from config import DEMO_TITLE, IS_SHARE, IS_DEBUG, CV_EXT, EXT_TXT
from config import CHEAP_API_BASE, CHEAP_API_KEY, CHEAP_MODEL
from config import STRONG_API_BASE, STRONG_API_KEY, STRONG_MODEL
from util import is_valid_url
from util import mylogger
from util import stream_together
# from util import checkAPI
from taskNonAI import extract_url, file_to_html, compile_pdf
from taskAI import TaskAI

## load data
from _data_test import mock_jd, mock_cv

## ui
import gradio as gr

## dependency
from pypandoc.pandoc_download import download_pandoc

## std
import os
import json

## debug
from icecream import ic

## platform specific
from _hf import HF, REPO_ID

logger = mylogger(__name__, "%(asctime)s:%(levelname)s:%(message)s")
info = logger.info


def init():
    try:
        os.system("shot-scraper install -b firefox")
        download_pandoc()
    except Exception as e:
        ic(e)
        if HF:
            HF.restart_space(REPO_ID)


## Config Functions


def set_same_cheap_strong(
    set_same: bool,
    cheap_base,
    cheap_key,
    cheap_model,
    strong_base,
    strong_key,
    strong_model,
):
    # setup_zone = gr.Accordion("AI setup (OpenAI-compatible LLM API)", open=True)
    if set_same:
        return (
            gr.Textbox(value=cheap_base, label="API Base", interactive=False),
            gr.Textbox(
                value=cheap_key, label="API key", type="password", interactive=False
            ),
            gr.Textbox(value=cheap_model, label="Model ID", interactive=False),
            # setup_zone,
        )
    else:
        return (
            gr.Textbox(value=strong_base, label="API Base", interactive=True),
            gr.Textbox(
                value=strong_key, label="API key", type="password", interactive=True
            ),
            gr.Textbox(value=strong_model, label="Model ID", interactive=True),
            # setup_zone,
        )


## Main Functions


def prepare_input(jd_info, cv_file: str, cv_text):
    if jd_info:
        if is_valid_url(jd_info):
            jd = extract_url(jd_info)
        else:
            jd = jd_info
    else:
        jd = mock_jd

    if cv_text:
        cv = cv_text
    elif cv_file:
        if any([cv_file.endswith(ext) for ext in EXT_TXT]):
            with open(cv_file, "r", encoding="utf8") as f:
                cv = f.read()
        else:
            cv = file_to_html(cv_file)
    else:
        cv = mock_cv
    return jd, cv


def run_refine(api_base, api_key, api_model, jd_info, cv_text):
    jd, cv = jd_info, cv_text
    cheapAPI = {"base": api_base, "key": api_key, "model": api_model}
    taskAI = TaskAI(cheapAPI, temperature=0.2, max_tokens=2048)  # max_tokens=2048
    info("API initialized")
    gen = stream_together(
        taskAI.jd_preprocess(input=jd),
        taskAI.cv_preprocess(input=cv),
    )
    for result in gen:
        yield result


def run_compose(api_base, api_key, api_model, min_jd, min_cv, is_debug):
    strongAPI = {"base": api_base, "key": api_key, "model": api_model}
    taskAI = TaskAI(strongAPI, is_debug=is_debug, temperature=0.6, max_tokens=4000)
    info("Composing letter with CoT ...")
    result = ""
    for response in taskAI.compose_letter_CoT(jd=min_jd, resume=min_cv):
        result += response.delta
        yield result


def finalize_letter_txt(api_base, api_key, api_model, debug_CoT):
    cheapAPI = {"base": api_base, "key": api_key, "model": api_model}
    taskAI = TaskAI(cheapAPI, temperature=0.2, max_tokens=2048)
    info("Finalizing letter ...")
    result = ""
    for response in taskAI.purify_letter(full_text=debug_CoT):
        result += response.delta
        yield result


def finalize_letter_pdf(
    api_base, api_key, api_model, jd, cv, cover_letter_text, is_debug
):
    cheapAPI = {"base": api_base, "key": api_key, "model": api_model}
    taskAI = TaskAI(cheapAPI, temperature=0.1, max_tokens=100)
    meta_data = next(taskAI.get_jobapp_meta(JD=jd, CV=cv))
    pdf_context = json.loads(meta_data)
    if is_debug:
        ic(pdf_context)
    pdf_context["letter_body"] = cover_letter_text
    return meta_data, compile_pdf(
        pdf_context,
        tmpl_path="app/typst/template_letter.tmpl",
        output_path=f"cover_letter_by_{pdf_context['applicantFullName']}_to_{pdf_context['companyFullName']}.pdf",
        is_debug=is_debug,
    )


with gr.Blocks(
    title=DEMO_TITLE,
    theme=gr.themes.Soft(
        primary_hue="sky", secondary_hue="emerald", neutral_hue="stone"
    ),
) as app:
    intro = f"""# {DEMO_TITLE}
    > You provide job description and résumé, and I write Cover letter for you!  

    **IMPORTANT** In order to enable AI capability, you have to ***BRING YOUR OWN API Key***. 
    """
    gr.Markdown(intro)
    with gr.Accordion("=== IMPORTANT: READ ME FIRST ===", open=False):
        guide = gr.Markdown("""## Setup

    > **IMPORTANT**: First setup **API Keys** for 2 AI agents, CheapAI and StrongAI, on the "AI Setup" panel before you start. If you know what you are doing, change other API configurations as well.

    + `API Key`: If you have no idea, go to https://beta.openai.com/account/api-keys  

    + `Model ID`: 
        - **CheapAI**: 
            + `gpt-3.5-turbo` any variant should be fine unless OpenAI make them lazier and dumber.  
            + `Mistral-7B-Instruct-v0.1` works well
            + `gemma-7b-it` usually can't understand instructions properly and cause error.
        - **StrongAI**: 
            + `Mistral-7B-Instruct-v0.1` can do the job.
            + Models with small context window size like won't work, such as
                - `gpt-3.5-turbo-0613`
                -  perhaps `gpt-4-0613`
    
    Model choice can be a interesting topic involing quite a few experiments. Feel free to try any other models you like!

    ## Troubleshooting
    - If your API is on localhost / local network, you may need to host this app on local network too.
    - If your API is on some AI service platform, review if you have enough balance / credits / quota on the platform.
    - If you are sure that you have set up the API correctly, but encounter an error along the way, try click the "Go!" button again.
    - Try change AI provider / model.
    - Report to [GitHub issue](https://github.com/cxumol/CoverPilot/issues) if you believe it's a bug.
""")
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Accordion(
                "AI setup (OpenAI-compatible LLM API)", open=False
            ) as setup_zone:
                is_debug = gr.Checkbox(label="Debug Mode", value=IS_DEBUG)

                gr.Markdown(
                    "**CheapAI**, an honest format converter and refiner, extracts essential info from job description and résumé, to reduce subsequent cost on Strong AI."
                )
                with gr.Group():
                    cheap_base = gr.Textbox(value=CHEAP_API_BASE, label="API Base")
                    cheap_key = gr.Textbox(
                        value=CHEAP_API_KEY, label="API key", type="password"
                    )
                    cheap_model = gr.Textbox(value=CHEAP_MODEL, label="Model ID")
                gr.Markdown(
                    "---\n**StrongAI**, a thoughtful wordsmith, generates perfect cover letters to make both you and recruiters happy."
                )
                is_same_cheap_strong = gr.Checkbox(
                    label="the same as Cheap AI", value=False, container=False
                )
                with gr.Group():
                    strong_base = gr.Textbox(value=STRONG_API_BASE, label="API Base")
                    strong_key = gr.Textbox(
                        value=STRONG_API_KEY, label="API key", type="password"
                    )
                    strong_model = gr.Textbox(value=STRONG_MODEL, label="Model ID")
            with gr.Group():
                gr.Markdown("## Employer - Job Description")
                jd_info = gr.Textbox(
                    label="Job Description",
                    placeholder="Paste as Full Text (recommmend) or URL",
                    lines=5,
                    max_lines=10,
                )
            with gr.Group():
                gr.Markdown("## Applicant - CV / Résumé")
                # with gr.Row():
                cv_file = gr.File(
                    label="Allowed formats: " + " ".join(CV_EXT),
                    file_count="single",
                    file_types=CV_EXT,
                    type="filepath",
                )
                cv_text = gr.TextArea(
                    label="Or enter text",
                    placeholder="If attempting to both upload a file and enter text, only this text will be used.",
                )
        with gr.Column(scale=2):
            gr.Markdown("## Result")
            with gr.Accordion("Reformatting", open=True) as reformat_zone:
                with gr.Row():
                    min_jd = gr.TextArea(label="Clean verion of Job Description")
                    min_cv = gr.TextArea(label="Clean verion of CV / Résumé")
            with gr.Accordion("Expert Zone", open=False) as expert_zone:
                debug_CoT = gr.Textbox(label="Chain of Thoughts")
                debug_jobapp = gr.Textbox(label="Job application meta data")
            cover_letter_text = gr.Textbox(label="Cover Letter")
            cover_letter_pdf = gr.File(
                label="Cover Letter PDF",
                file_count="multiple",
                type="filepath",
            )
            infer_btn = gr.Button("Go!", variant="primary")
            gr.Markdown("#### Like it? Give me a star ⭐ [on GitHub](https://github.com/cxumol/CoverPilot)!")

    is_same_cheap_strong.change(
        fn=set_same_cheap_strong,
        inputs=[
            is_same_cheap_strong,
            cheap_base,
            cheap_key,
            cheap_model,
            strong_base,
            strong_key,
            strong_model,
        ],
        outputs=[strong_base, strong_key, strong_model],
    ).then(
        fn=lambda: gr.Accordion("AI setup (OpenAI-compatible LLM API)", open=True),
        inputs=None,
        outputs=[setup_zone],
    )

    infer_btn.click(
        fn=set_same_cheap_strong,
        inputs=[
            is_same_cheap_strong,
            cheap_base,
            cheap_key,
            cheap_model,
            strong_base,
            strong_key,
            strong_model,
        ],
        outputs=[strong_base, strong_key, strong_model],
    ).then(
        fn=lambda: gr.Accordion("AI setup (OpenAI-compatible LLM API)", open=False),
        inputs=None,
        outputs=[setup_zone],
    ).success(
        fn=prepare_input, inputs=[jd_info, cv_file, cv_text], outputs=[jd_info, cv_text]
    ).success(
        fn=lambda: gr.Accordion("Reformatting", open=True),
        inputs=None,
        outputs=[reformat_zone],
    ).success(
        fn=run_refine,
        inputs=[cheap_base, cheap_key, cheap_model, jd_info, cv_text],
        outputs=[min_jd, min_cv],
    ).success(
        fn=lambda: [
            gr.Accordion("Expert Zone", open=True),
            gr.Accordion("Reformatting", open=False),
        ],
        inputs=None,
        outputs=[expert_zone, reformat_zone],
    ).success(
        fn=run_compose,
        inputs=[strong_base, strong_key, strong_model, min_jd, min_cv, is_debug],
        outputs=[debug_CoT],
    ).success(
        fn=lambda: gr.Accordion("Expert Zone", open=False),
        inputs=None,
        outputs=[expert_zone],
    ).success(
        fn=finalize_letter_txt,
        inputs=[cheap_base, cheap_key, cheap_model, debug_CoT],
        outputs=[cover_letter_text],
    ).success(
        fn=finalize_letter_pdf,
        inputs=[
            cheap_base,
            cheap_key,
            cheap_model,
            jd_info,
            cv_text,
            cover_letter_text,
            is_debug,
        ],
        outputs=[debug_jobapp, cover_letter_pdf],
    )


if __name__ == "__main__":
    init()
    app.queue(max_size=1, default_concurrency_limit=1).launch(
        show_error=True, debug=True, share=IS_SHARE
    )
