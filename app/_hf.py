import os

from huggingface_hub import HfApi

HF_TOKEN = os.environ.get("HF_TOKEN", None)
REPO_ID = os.environ.get("REPO_ID", None)

HF = None
if HF_TOKEN:
    HF = HfApi(token=HF_TOKEN)