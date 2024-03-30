import os

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""

CHEAP_API_BASE = os.getenv("CHEAP_API_BASE") or OPENAI_API_BASE
CHEAP_API_KEY = os.getenv("CHEAP_API_KEY") or OPENAI_API_KEY
CHEAP_MODEL = os.getenv("CHEAP_MODEL") or "gpt-3.5-turbo"

STRONG_API_BASE = os.getenv("STRONG_API_BASE") or OPENAI_API_BASE
STRONG_API_KEY = os.getenv("STRONG_API_KEY") or OPENAI_API_KEY
STRONG_MODEL = os.getenv("STRONG_MODEL") or "gpt-4"

IS_SHARE = bool(os.getenv("IS_SHARE")) or False
IS_DEBUG = bool(os.getenv("IS_DEBUG")) or False

DEMO_TITLE = "Cover Letter Generator"
DEMO_DESCRIPTION = "This is a demo of the OpenAI API for generating cover letters. The model is trained on a dataset of cover letters and job descriptions, and generates a cover letter based on the job description and the applicant's CV. The model is fine-tuned on the OpenAI API, and is able to generate cover letters that are tailored to the job description and the applicant's CV. The model is able to generate cover letters for a wide range of jobs, and is able to generate cover letters that are tailored to the job description and the applicant's CV. The model is able to generate cover letters for a wide range of jobs, and is able to generate cover letters that are tailored to the job description and the applicant's CV. The model is able to generate cover letters for a wide range of jobs, and is able to generate cover letters that are tailored to the job description and the applicant's CV."

CV_EXT = [".typ", ".tex", ".html", ".docx", ".rst", ".rtf", ".odt", ".txt", ".md"]
EXT_TXT = [".txt", ".md"]
