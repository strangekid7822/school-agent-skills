#!/usr/bin/env python3
"""
TestPaperGenerator_DanxiangxuanzeCombination
Combines 单项选择 questions from multiple structured txt files into a
single formatted A4 PDF (no answers, vocabulary, or translations).

Usage:
    python generate.py file1.txt file2.txt ... --output STEM [--output-dir DIR]

    --output   Output file stem (no extension).  Default: first file's stem.
    --output-dir  Directory for .html / .pdf output.  Default: directory of
                  the first input file.
"""

import argparse
import html as html_module
import re
import subprocess
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent  # .agent/skills/
LOGO_PATH  = SKILLS_DIR / "SchoolWork_WordTestGenerator" / "resources" / "teacher_logo.jpg"
PDF_JS     = SKILLS_DIR / "SchoolWork_WordTestGenerator" / "scripts" / "html_to_pdf.js"


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
@page { size: A4; margin: 12mm 14mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Noto Sans SC', sans-serif;
    font-size: 10.5pt;
    color: #1a1a1a;
    background: #fff;
    line-height: 1.65;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
.page { width: 100%; }

/* Header */
.doc-header {
    border-bottom: 2.5px solid #111;
    padding-bottom: 10px;
    margin-bottom: 18px;
}
.doc-header-row { display: flex; align-items: center; gap: 14px; }
.doc-logo {
    width: 46px; height: 46px; border-radius: 50%;
    object-fit: cover; flex-shrink: 0; border: 1.5px solid #ddd;
}
.doc-title { font-size: 14.5pt; font-weight: 800; color: #111; line-height: 1.25; letter-spacing: 0.01em; }
.doc-subtitle { font-size: 8.5pt; color: #888; margin-top: 3px; letter-spacing: 0.12em; }

/* Paper source label */
.paper-label {
    font-size: 7pt;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #999;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4px;
    margin-bottom: 12px;
    margin-top: 18px;
}
.paper-label:first-child { margin-top: 0; }

/* Questions */
.question-block {
    margin-bottom: 11px;
    page-break-inside: avoid;
}
.question-row {
    display: flex;
    align-items: flex-start;
    gap: 0;
    margin-bottom: 3px;
    line-height: 1.65;
}
.q-prefix {
    font-size: 10.5pt;
    color: #111;
    flex-shrink: 0;
    white-space: nowrap;
    line-height: 1.65;
    min-width: 3em;
    display: inline-block;
}
.q-num { font-weight: 700; }
.q-text {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10.5pt;
    color: #111;
    line-height: 1.65;
}

.q-body {
    flex: 1;
    min-width: 0;
}

/* Options */
.opts-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1px;
    box-sizing: border-box;
    table-layout: fixed;
}
.opt-td {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10.5pt;
    color: #333;
    vertical-align: top;
    padding: 1px 6px 1px 0;
    line-height: 1.6;
    word-break: break-word;
}
.opt-letter {
    color: #111;
    font-size: 10.5pt;
    margin-right: 2px;
}

.opts-stacked { margin-top: 1px; }
.opt-stack {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10.5pt;
    color: #333;
    line-height: 1.6;
}

@media print {
    .question-block { page-break-inside: avoid; }
}
"""

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>{css}</style>
</head>
<body>
<div class="page">
{content}
</div>
</body>
</html>
"""


# ── Parser ────────────────────────────────────────────────────────────────────

def e(text):
    return html_module.escape(str(text))


def parse_questions(filepath):
    text = Path(filepath).read_text(encoding='utf-8')
    m = re.search(r'【单项选择·(?:习题|题目)】\s*\n(.*?)(?=【|={5,})', text, re.DOTALL)
    if not m:
        print(f"  WARNING: no question section found in {Path(filepath).name}")
        return []

    section = m.group(1)
    raw_blocks = re.split(r'(?=\(\s*\)\s*\d+\.)', section)

    questions = []
    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue
        qm = re.match(r'\(\s*\)\s*(\d+)\.\s+(.*)', block, re.DOTALL)
        if not qm:
            continue

        rest_lines = qm.group(2).split('\n')
        q_text_parts = []
        opts_raw = []
        in_opts = False

        for line in rest_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r'^[A-D]\.', stripped):
                in_opts = True
            if in_opts:
                opts_raw.append(stripped)
            else:
                q_text_parts.append(stripped)

        # Join dialogue lines (starting with —) with <br>, others with space
        joined_parts = []
        for part in q_text_parts:
            if joined_parts and (part.startswith('—') or joined_parts[-1].startswith('—')):
                joined_parts.append('<br>' + html_module.escape(part))
            else:
                if joined_parts:
                    joined_parts.append(' ' + html_module.escape(part))
                else:
                    joined_parts.append(html_module.escape(part))
        q_text = ''.join(joined_parts)

        opts = []
        if len(opts_raw) == 1:
            # Split before B./C./D. on any whitespace; A. is always the start
            parts = re.split(r'\s+(?=[B-D]\.)', opts_raw[0])
            for part in parts:
                pm = re.match(r'^([A-D])\.\s*(.+)', part.strip())
                if pm:
                    opts.append((pm.group(1), pm.group(2).strip()))
        else:
            for ol in opts_raw:
                parts = re.split(r'\s{2,}(?=[A-D]\.)', ol)
                for part in parts:
                    pm = re.match(r'^([A-D])\.\s*(.+)', part.strip())
                    if pm:
                        opts.append((pm.group(1), pm.group(2).strip()))

        questions.append({'text': q_text, 'opts': opts})

    return questions


# ── HTML rendering ─────────────────────────────────────────────────────────────

def render_question(global_num, q):
    opts = q['opts']
    if not opts:
        opts_html = ''
    elif any(len(txt) > 20 for _, txt in opts):
        # Stack each option on its own line
        rows = ''.join(
            f'<div class="opt-stack"><span class="opt-letter">{e(ltr)}.</span>{e(txt)}</div>'
            for ltr, txt in opts
        )
        opts_html = f'<div class="opts-stacked">{rows}</div>'
    else:
        n = len(opts)
        col_pct = f'{100 // n}%'
        cells = ''.join(
            f'<td class="opt-td" width="{col_pct}">'
            f'<span class="opt-letter">{e(ltr)}.</span>{e(txt)}'
            f'</td>'
            for ltr, txt in opts
        )
        opts_html = f'<table class="opts-table"><tr>{cells}</tr></table>'

    return (
        f'<div class="question-block">'
        f'<div class="question-row">'
        f'<span class="q-prefix">( &nbsp;)&nbsp;<span class="q-num">{global_num}.</span>&nbsp;</span>'
        f'<div class="q-body">'
        f'<span class="q-text">{q["text"]}</span>'
        f'{opts_html}'
        f'</div>'
        f'</div>'
        f'</div>'
    )


def generate_html(all_paper_questions, title, subtitle, start_paper_index=1):
    logo_html = f'<img src="file://{LOGO_PATH}" class="doc-logo" alt="">' if LOGO_PATH.exists() else ''
    header = (
        f'<div class="doc-header">'
        f'<div class="doc-header-row">'
        f'{logo_html}'
        f'<div>'
        f'<div class="doc-title">{e(title)}</div>'
        f'<div class="doc-subtitle">{e(subtitle)}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )

    parts = [header]
    global_num = 1
    for paper_idx, questions in enumerate(all_paper_questions, start=start_paper_index):
        parts.append(f'<div class="paper-label">试卷 {paper_idx}</div>')
        for q in questions:
            parts.append(render_question(global_num, q))
            global_num += 1

    content = '\n'.join(parts)
    return HTML_TEMPLATE.format(css=CSS, content=content)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Combine 单项选择 txt files into one PDF.')
    parser.add_argument('inputs', nargs='+', help='Input .txt files (one per 试卷)')
    parser.add_argument('--output', default=None,
                        help='Output file stem (no extension). Default: first input stem.')
    parser.add_argument('--output-dir', default=None,
                        help='Output directory. Default: directory of first input file.')
    parser.add_argument('--title', default='英语单项选择综合卷',
                        help='Document title. Default: 英语单项选择综合卷')
    parser.add_argument('--start', type=int, default=1,
                        help='Starting 试卷 index label. Default: 1')
    args = parser.parse_args()

    input_paths = [Path(p) for p in args.inputs]
    output_dir  = Path(args.output_dir) if args.output_dir else input_paths[0].parent
    output_stem = args.output or input_paths[0].stem

    n = len(input_paths)
    end_idx = args.start + n - 1
    range_str = str(args.start) if n == 1 else f'{args.start}–{end_idx}'
    subtitle = f'中考模拟题库 · 试卷 {range_str}'

    all_paper_questions = []
    for fpath in input_paths:
        print(f'Parsing {fpath.name}...')
        qs = parse_questions(fpath)
        print(f'  → {len(qs)} questions')
        all_paper_questions.append(qs)

    html_content = generate_html(all_paper_questions, args.title, subtitle, args.start)

    html_path = output_dir / f'{output_stem}.html'
    pdf_path  = output_dir / f'{output_stem}.pdf'

    html_path.write_text(html_content, encoding='utf-8')
    print(f'HTML: {html_path}')

    result = subprocess.run(
        ['node', str(PDF_JS), str(html_path), str(pdf_path)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f'PDF:  {pdf_path}')
    else:
        print(f'PDF conversion failed:\n{result.stderr}')
        raise SystemExit(1)


if __name__ == '__main__':
    main()
