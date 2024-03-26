import pypandoc
## stdlib
import subprocess
import json
from typing import Optional

def file_to_html(file_path: str) -> str:
    return pypandoc.convert_file(file_path, "html")


def extract_url(url: str) -> Optional[str]:
    cmd = f"""shot-scraper javascript -b firefox \
      "{url}" "
    async () => {{
      const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
      return (new readability.Readability(document)).parse();
    }}"
"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        result.check_returncode()
    except:
        raise Exception(
            f"Please try copy-paste as input. Failed to extract content from url: {url}. Error: {result.stderr}"
        )
    result = json.loads(result.stdout)
    try:
        return result["textContent"]
    except:
        raise Exception(
            f"Please try copy-paste as input. Failed to extract content from: {url}. Didn't find content from given URL!"
        )