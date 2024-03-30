import pypandoc
import typst

## stdlib
import subprocess
import json
import os
from typing import Optional
from string import Template

from datetime import datetime
from pathlib import Path


def file_to_html(file_path: str) -> str:
    return pypandoc.convert_file(file_path, "html")


def extract_url(url: str) -> Optional[str]:
    cmd = f"""shot-scraper javascript -b firefox \
      "{url}" "
    async () => {{
      const sleep = duration => new Promise(resolve => setTimeout(() => resolve(), duration));
      const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
      await sleep(3000);
      return new readability.Readability(document).parse();
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


def _date() -> str:
    current_date = datetime.now()
    return current_date.strftime(
        f"%B %d{'th' if 4 <= current_date.day <= 20 or 24 <= current_date.day <= 30 else ['st', 'nd', 'rd'][current_date.day % 10 - 1]} , %Y"
    )


def _typst_escape(s) -> str:
    return str(s).replace("@", "\@").replace("#", "\#")


def compile_pdf(
    context: dict, tmpl_path: str, output_path="/tmp/cover_letter.pdf", is_debug=False
) -> list[str]:
    letter_src_filepath = "typst/letter.typ"
    with open(tmpl_path, "r", encoding="utf8") as f:
        tmpl = Template(f.read())
    context = {k: _typst_escape(v) for k, v in context.items()}
    context.update({"date_string": _date()})
    letter_typ = tmpl.safe_substitute(context)
    with open(letter_src_filepath, "w", encoding="utf8") as f:
        f.write(letter_typ)
    typst.compile(
        letter_src_filepath,
        output_path,
        root=Path("./typst/"),
        font_paths=[Path("./fonts/")],
    )
    # os.remove(letter_src_filepath)
    if is_debug:
        return [letter_src_filepath, output_path]
    else:
        return [output_path]
