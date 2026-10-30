from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
app = FastAPI(title="Text to LaTeX Converter")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

class ConvertRequest(BaseModel):
    text: str

def esc(s: str) -> str:
    return re.sub(r"([\\{}%$&#_])", r"\\\1", s)

def convert_to_latex(text: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    out = [r"\documentclass[11pt]{article}", r"\usepackage[utf8]{inputenc}", r"\usepackage[T1]{fontenc}", r"\usepackage{enumitem}", "", r"\begin{document}", ""]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        m = re.match(r"^(#{1,3})\s+(.+)$", line)
        if m:
            cmd = {1:"section",2:"subsection",3:"subsubsection"}[len(m.group(1))]
            out += [f"\\{cmd}{{{esc(m.group(2))}}}", ""]; i += 1; continue
        if re.match(r"^(?:[-*•]|\d+[.)])\s+", line):
            ordered = bool(re.match(r"^\d+[.)]\s+", line)); env = "enumerate" if ordered else "itemize"
            out.append(f"\\begin{{{env}}}")
            while i < len(lines) and re.match(r"^(?:[-*•]|\d+[.)])\s+", lines[i].strip()):
                out.append("  \\item " + esc(re.sub(r"^(?:[-*•]|\d+[.)])\s+", "", lines[i].strip()))); i += 1
            out += [f"\\end{{{env}}}", ""]; continue
        if i == 0 and len(line) <= 120 and not line.endswith((".","!","?",":")):
            out += [f"\\title{{{esc(line)}}}", r"\maketitle", ""]; i += 1; continue
        para = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(?:#{1,3}\s+|(?:[-*•]|\d+[.)])\s+)", lines[i].strip()): para.append(lines[i].strip()); i += 1
        out += [esc(" ".join(para)), ""]
    out.append(r"\end{document}")
    return "\n".join(out)

@app.get("/", response_class=HTMLResponse)
def index(): return (BASE / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/api/convert")
def convert(request: ConvertRequest): return {"latex": convert_to_latex(request.text)}
