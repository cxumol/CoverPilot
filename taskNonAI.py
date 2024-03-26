import pypandoc
import typst
## stdlib
import subprocess
import json
import os
from typing import Optional
from string import Template

from datetime import datetime


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

def date():
    current_date = datetime.now()
    return current_date.strftime(
        f"%B %d{'th' if 4 <= current_date.day <= 20 or 24 <= current_date.day <= 30 else ['st', 'nd', 'rd'][current_date.day % 10 - 1]} , %Y")

def typst_escape(s):
    return s.replace('@','\@').replace('#','\#')

def compile_pdf(context: dict, tmpl_path: str, output_path="/tmp/cover_letter.pdf"):
    with open(tmpl_path, "r", encoding='utf8') as f:
        tmpl = Template(f.read())
    context = {k: typst_escape(v) for k, v in context.items()}
    context.update({'date_string': date()})
    letter_typ = tmpl.safe_substitute(context)
    with open('letter.typ', 'w', encoding='utf8') as f:
        f.write(letter_typ)
    typst.compile('letter.typ', output=output_path)
    os.remove('letter.typ')
    return output_path