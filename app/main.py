from pathlib import Path
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE = Path(__file__).resolve().parent
app = FastAPI(title="Text to LaTeX Converter")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

class ConvertRequest(BaseModel):
    text: str
    purpose: str = "report"

PURPOSES = {
    "report": {"class": "article", "options": "11pt", "packages": ["geometry"], "title": "report"},
    "business": {"class": "article", "options": "11pt", "packages": ["geometry", "xcolor"], "title": "business"},
    "academic": {"class": "article", "options": "12pt", "packages": ["geometry", "amsmath", "amssymb", "cite"], "title": "academic"},
    "presentation": {"class": "beamer", "options": "aspectratio=169", "packages": ["professionalfont"], "title": "presentation"},
}

def esc(value: str) -> str:
    return re.sub(r"([\\{}%$&#_])", r"\\\1", value)

def convert_to_latex(text: str, purpose: str = "report") -> str:
    preset = PURPOSES.get(purpose, PURPOSES["report"])
    lines = text.replace("\r\n", "\n").split("\n")
    out = [f"\\documentclass[{preset['options']}]{{{preset['class']}}}", r"\usepackage[utf8]{inputenc}", r"\usepackage[T1]{fontenc}", r"\usepackage{enumitem}"]
    out += [f"\\usepackage{{{package}}}" for package in preset["packages"]] + ["", r"\begin{document}", ""]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            command = {1: "section", 2: "subsection", 3: "subsubsection"}[len(heading.group(1))]
            out += [f"\\{command}{{{esc(heading.group(2))}}}", ""]; i += 1; continue
        if re.match(r"^(?:[-*]|\d+[.)])\s+", line):
            ordered = bool(re.match(r"^\d+[.)]\s+", line)); environment = "enumerate" if ordered else "itemize"
            out.append(f"\\begin{{{environment}}}")
            while i < len(lines) and re.match(r"^(?:[-*]|\d+[.)])\s+", lines[i].strip()):
                out.append("  \\item " + esc(re.sub(r"^(?:[-*]|\d+[.)])\s+", "", lines[i].strip()))); i += 1
            out += [f"\\end{{{environment}}}", ""]; continue
        if i == 0 and len(line) <= 120 and not line.endswith((".", "!", "?", ":")):
            out += [f"\\title{{{esc(line)}}}", r"\maketitle", ""]; i += 1; continue
        paragraph = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(?:#{1,3}\s+|(?:[-*]|\d+[.)])\s+)", lines[i].strip()): paragraph.append(lines[i].strip()); i += 1
        out += [esc(" ".join(paragraph)), ""]
    out.append(r"\end{document}")
    return "\n".join(out)

@app.get("/", response_class=HTMLResponse)
def index(): return (BASE / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/api/convert")
def convert(request: ConvertRequest):
    purpose = request.purpose if request.purpose in PURPOSES else "report"
    return {"latex": convert_to_latex(request.text, purpose), "purpose": purpose, "template": PURPOSES[purpose]["title"]}
