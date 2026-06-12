#!/usr/bin/env python3
"""
TestPaperGenerator v5

Changes from v4:
  - 阅读理解·习题: parsed into individual questions; adaptive option layout —
    one row when all options are short (total chars ≤ 72), otherwise one per line
  - 重点词汇 (question side): always shown as English practice grid regardless of whether
    Chinese meanings exist; English words extracted from "word - meaning" lines
  - Version suffix changed to _v5.

Usage: python generate_pdf_v5.py <input.txt> [output_dir]
"""

import sys
import re
import html as html_module
import subprocess
from pathlib import Path

DEFAULT_OUTPUT = Path("/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/11_SkillWorkSpace")
SCRIPTS_DIR = Path(__file__).parent
SKILL_DIR = SCRIPTS_DIR.parent

LOGO_PATH = SKILL_DIR.parent / "SchoolWork_WordTestGenerator" / "resources" / "teacher_logo.jpg"

_local_js = SCRIPTS_DIR / "html_to_pdf.js"
_wt_js = SKILL_DIR.parent / "SchoolWork_WordTestGenerator" / "scripts" / "html_to_pdf.js"

def find_pdf_js():
    if (_local_js.parent / "node_modules").exists() and _local_js.exists():
        return _local_js
    if _wt_js.exists() and (_wt_js.parent / "node_modules").exists():
        return _wt_js
    return _local_js


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

.page {
    width: 100%;
}

/* ── Document Header ── */
.doc-header {
    border-bottom: 2.5px solid #111;
    padding-bottom: 10px;
    margin-bottom: 18px;
}
.doc-header-row {
    display: flex;
    align-items: center;
    gap: 14px;
}
.doc-logo {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
    border: 1.5px solid #ddd;
}
.doc-title {
    font-size: 14.5pt;
    font-weight: 800;
    color: #111;
    line-height: 1.25;
    letter-spacing: 0.01em;
}
.doc-subtitle {
    font-size: 8.5pt;
    color: #888;
    margin-top: 3px;
    letter-spacing: 0.12em;
}

/* ── Section ── */
.section {
    margin-bottom: 13px;
}
.section-label {
    font-size: 7pt;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #999;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4px;
    margin-bottom: 10px;
}

/* ── Passage ── */
.passage-title {
    font-size: 12.5pt;
    font-weight: 700;
    color: #111;
    text-align: center;
    margin-bottom: 11px;
    font-family: Georgia, 'Times New Roman', serif;
    letter-spacing: 0.01em;
}
.passage-para {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10pt;
    color: #222;
    line-height: 1.7;
    text-indent: 2em;
    margin-bottom: 5px;
}
.blank {
    font-family: 'Courier New', Courier, monospace;
    font-size: 10pt;
    color: #444;
    letter-spacing: -0.02em;
}
.blank-inner {
    font-weight: 700;
    color: #111;
    letter-spacing: 0;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 9.5pt;
}
.passage-underline {
    text-decoration: underline;
    text-underline-offset: 2px;
}
.passage-bold {
    font-weight: 700;
    color: #111;
}

/* ── Reading Comprehension Questions ── */
.reading-question {
    margin-bottom: 11px;
    page-break-inside: avoid;
}
.reading-q-text {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10.5pt;
    color: #111;
    line-height: 1.65;
    margin-bottom: 5px;
}
.reading-q-num {
    font-weight: 700;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
}
.reading-opts-table {
    width: 100%;
    border-collapse: collapse;
}
/* one-row layout: fixed equal-width columns so options align across all
   questions (every column starts at the same x-position, regardless of text) */
.reading-opts-table.one-row { table-layout: fixed; }
.reading-opts-table.one-row .reading-opt-cell {
    padding: 2px 12px 2px 0;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10pt;
    color: #333;
    vertical-align: top;
    line-height: 1.6;
    white-space: nowrap;
}
/* per-line layout: each option occupies the full width */
.reading-opts-table.per-line .reading-opt-cell {
    width: 100%;
    display: block;
    padding: 1px 0;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10pt;
    color: #333;
    line-height: 1.6;
}
.reading-opt-letter {
    font-weight: 700;
    color: #111;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    margin-right: 2px;
}

/* ── Options (single-column box — for 七选五) ── */
.options-box {
    border: 1.5px solid #c8c8c8;
    border-radius: 3px;
    padding: 4px 14px;
    background: #fafafa;
}
.option-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 4px 0;
    border-bottom: 1px dotted #e0e0e0;
}
.option-item:last-child {
    border-bottom: none;
    padding-bottom: 1px;
}
.option-letter {
    font-size: 9.5pt;
    font-weight: 700;
    color: #111;
    flex-shrink: 0;
    width: 20px;
    padding-top: 1px;
}
.option-text {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10pt;
    color: #333;
    line-height: 1.6;
}

/* ── Word Bank (选词填空) ── */
.wordbank-box {
    border: 1.5px solid #555;
    border-radius: 3px;
    padding: 8px 16px;
    margin-bottom: 13px;
    background: #fafafa;
}
.wordbank-row {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 4px 18px;
    padding: 3px 0;
}
.wordbank-word {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10.5pt;
    color: #111;
    white-space: nowrap;
}

/* ── Translation Practice (question side) ── */
.trans-practice-item {
    margin-bottom: 16px;
    padding-bottom: 14px;
    border-bottom: 1px dotted #ddd;
}
.trans-practice-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
}
.trans-practice-prompt {
    font-size: 9pt;
    color: #666;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}
.trans-practice-en {
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    font-size: 10.5pt;
    color: #111;
    line-height: 1.8;
    margin-bottom: 10px;
    padding-left: 4px;
}
.write-line {
    border-bottom: 1px solid #bbb;
    height: 24px;
    margin-bottom: 4px;
}

/* ── Answer Section Divider ── */
.answer-divider {
    page-break-before: always;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 4mm;
    margin-bottom: 16px;
}
.answer-divider-line {
    flex: 1;
    height: 1.5px;
    background: #111;
}
.answer-divider-text {
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.35em;
    color: #333;
    white-space: nowrap;
    text-transform: uppercase;
}

/* ── Answers ── */
.answers-container {
    display: flex;
    flex-direction: column;
    gap: 7px;
}
.answer-entry {
    background: #f7f7f7;
    border-left: 3px solid #b0b0b0;
    padding: 8px 11px;
}
.answer-header {
    display: flex;
    align-items: baseline;
    gap: 7px;
    margin-bottom: 4px;
    flex-wrap: wrap;
}
.answer-num {
    font-size: 8.5pt;
    font-weight: 700;
    color: #aaa;
    flex-shrink: 0;
    min-width: 22px;
}
.answer-letter-big {
    font-size: 14pt;
    font-weight: 900;
    color: #111;
    flex-shrink: 0;
    line-height: 1;
    min-width: 18px;
}
.answer-word {
    font-size: 11pt;
    font-weight: 700;
    font-style: italic;
    color: #111;
    flex-shrink: 0;
}
.answer-note {
    font-size: 8pt;
    color: #999;
    letter-spacing: 0.04em;
    line-height: 1.4;
}
.answer-jiexi {
    font-size: 9.5pt;
    color: #444;
    line-height: 1.65;
    padding-left: 47px;
}
.answer-extra {
    margin-top: 6px;
    padding: 6px 9px;
    background: #fff;
    border-top: 1px solid #e0e0e0;
    font-size: 9pt;
    color: #555;
    line-height: 1.6;
}
.extra-line { margin-bottom: 2px; }
.tag-label { font-weight: 700; color: #666; }

/* ── Vocabulary ── */
.vocab-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 3px 18px;
}
.vocab-item {
    font-size: 9.5pt;
    padding: 3px 0;
    border-bottom: 1px solid #f0f0f0;
    line-height: 1.5;
}
.vocab-en { font-weight: 600; color: #111; }
.vocab-sep { color: #bbb; margin: 0 3px; }
.vocab-cn { color: #666; font-size: 9pt; }

/* ── Translation (answer side) ── */
.trans-block { margin-bottom: 13px; }
.trans-en {
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    font-size: 10pt;
    color: #222;
    line-height: 1.75;
    margin-bottom: 4px;
}
.trans-cn {
    font-size: 10pt;
    color: #333;
    font-style: italic;
    display: inline-block;
    border-bottom: 1.5px solid #555;
    padding-bottom: 2px;
    line-height: 1.8;
}

/* ── Vocab Practice (question side) ── */
.vocab-practice-prompt {
    font-size: 9pt;
    color: #666;
    letter-spacing: 0.04em;
    margin-bottom: 10px;
}
.vocab-practice-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0 20px;
}
.vocab-practice-item {
    display: flex;
    align-items: flex-end;
    gap: 5px;
    padding: 5px 0 2px;
    border-bottom: 1px solid #ccc;
}
.vocab-practice-word {
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    font-size: 10pt;
    color: #111;
    white-space: nowrap;
    flex-shrink: 0;
    line-height: 1.4;
}
.vocab-practice-fill { flex: 1; }

/* ── Cloze Options Grid (完形填空) ── */
.cloze-options-table {
    width: 100%;
    border-collapse: collapse;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10pt;
}
.cloze-option-row td {
    padding: 2.5px 10px 2.5px 0;
    vertical-align: top;
    line-height: 1.55;
    color: #222;
}
.cloze-q-num {
    font-weight: 700;
    color: #444;
    font-size: 9pt;
    white-space: nowrap;
    width: 26px;
    padding-left: 0;
}
.cloze-opt-label {
    font-weight: 700;
    color: #111;
    margin-right: 3px;
}
.cloze-opt-cell {
    /* no fixed width — browser distributes evenly */
}

/* ── Generic ── */
.generic-para {
    font-size: 10pt;
    color: #333;
    line-height: 1.65;
    margin-bottom: 6px;
}

/* ── Multiple Choice (单项选择) ── */
.mc-question {
    margin-bottom: 11px;
    page-break-inside: avoid;
}
.mc-q-header {
    display: flex;
    align-items: flex-start;
    gap: 5px;
    margin-bottom: 5px;
}
.mc-answer-slot {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10pt;
    color: #111;
    flex-shrink: 0;
    white-space: nowrap;
    letter-spacing: 0.05em;
    padding-top: 1px;
}
.mc-q-num {
    font-weight: 400;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10.5pt;
    flex-shrink: 0;
    padding-top: 1px;
}
.mc-q-body {
    flex: 1 1 auto;
    min-width: 0;
}
.mc-q-text {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 10.5pt;
    color: #111;
    line-height: 1.65;
}
.mc-q-body .reading-opts-table { margin-top: 4px; }
/* 单项选择: option letters share the question-text font and are not bold */
.mc-q-body .reading-opt-letter {
    font-family: Georgia, 'Times New Roman', serif;
    font-weight: 400;
}
.mc-blank {
    display: inline-block;
    border-bottom: 1.5px solid #444;
    min-width: 40px;
    margin: 0 2px;
    vertical-align: bottom;
}

@media print {
    body { background: #fff; }
    .answer-entry { page-break-inside: avoid; }
    .trans-practice-item { page-break-inside: avoid; }
    .cloze-option-row { page-break-inside: avoid; }
    .reading-question { page-break-inside: avoid; }
    .mc-question { page-break-inside: avoid; }
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


# ── Parser ──────────────────────────────────────────────────────────────────

def parse_file(filepath):
    text = Path(filepath).read_text(encoding='utf-8')
    lines = text.split('\n')

    title = ''
    for line in lines:
        s = line.strip()
        if s and not s.startswith('='):
            title = s
            break

    sections = []
    current_name = None
    current_lines = []

    for line in lines:
        s = line.strip()
        if s.startswith('==='): continue
        m = re.match(r'^【(.+?)】\s*$', s)
        if m:
            if current_name is not None:
                sections.append({'name': current_name, 'content': '\n'.join(current_lines).strip()})
            current_name = m.group(1)
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)

    if current_name is not None:
        sections.append({'name': current_name, 'content': '\n'.join(current_lines).strip()})

    return title, sections


# ── Helpers ──────────────────────────────────────────────────────────────────

def e(text):
    return html_module.escape(str(text))


def is_passage_title(text):
    if '___' in text:
        return False
    if any('\u4e00' <= c <= '\u9fa5' for c in text):
        return False
    return len(text) <= 50


def process_passage_text(text):
    """Escape and apply inline formatting markers for passage paragraphs:
    __...__ → underline, **...** → bold, ___N___ → numbered blank.
    Order matters: escape HTML first, then apply markers left-to-right.
    Bold+underline (**__...__**) is supported via nesting.
    """
    escaped = e(text)
    # Protect numbered blanks FIRST with underscore-free placeholders, so the
    # bold/underline passes below cannot match the blank's own underscores
    # (e.g. the underline regex would otherwise eat '___61___' → '_61_').
    blanks = []
    def _stash(m):
        blanks.append(m.group(1))
        return f'\x00BLK{len(blanks) - 1}\x00'
    escaped = re.sub(r'___(\d+)___', _stash, escaped)
    # Bold+underline combined: **__...__**
    escaped = re.sub(
        r'\*\*__(.+?)__\*\*',
        r'<span class="passage-bold passage-underline">\1</span>',
        escaped
    )
    # Bold only: **...**
    escaped = re.sub(
        r'\*\*(.+?)\*\*',
        r'<span class="passage-bold">\1</span>',
        escaped
    )
    # Underline only: __...__ (content must start with a non-underscore to avoid
    # matching runs of underscores used as fill-in blanks, e.g. ________)
    escaped = re.sub(
        r'__([^_].*?)__',
        r'<span class="passage-underline">\1</span>',
        escaped
    )
    # Restore numbered blanks as styled spans.
    escaped = re.sub(
        r'\x00BLK(\d+)\x00',
        lambda m: f'<span class="blank">___<span class="blank-inner">{blanks[int(m.group(1))]}</span>___</span>',
        escaped
    )
    return escaped


def process_blanks(text):
    """Legacy alias — used outside passage context (no formatting markers expected)."""
    escaped = e(text)
    return re.sub(
        r'___(\d+)___',
        r'<span class="blank">___<span class="blank-inner">\1</span>___</span>',
        escaped
    )


def has_chinese_meanings(content):
    """True if any vocab line contains a word-meaning separator ( - or –)."""
    return any(re.search(r'\s[-–]\s', line) for line in content.split('\n') if line.strip())


def extract_english_from_vocab_line(line):
    """Extract English word/phrase from a vocab line like 'pollution - n. 污染'."""
    m = re.match(r'^(.+?)\s+[-–]\s+', line)
    if m:
        return m.group(1).strip()
    return line.strip()


# ── Question-Side Renderers ──────────────────────────────────────────────────

def render_passage(name, content):
    paragraphs, current = [], []
    for line in content.split('\n'):
        if line.strip():
            current.append(line.strip())
        else:
            if current:
                paragraphs.append(' '.join(current))
                current = []
    if current:
        paragraphs.append(' '.join(current))

    if not paragraphs:
        return ''

    html_parts = []
    if is_passage_title(paragraphs[0]):
        html_parts.append(f'<p class="passage-title">{e(paragraphs[0])}</p>')
        body_paras = paragraphs[1:]
    else:
        body_paras = paragraphs

    for p in body_paras:
        html_parts.append(f'<p class="passage-para">{process_passage_text(p)}</p>')

    return f'<section class="section">{"".join(html_parts)}</section>'


def parse_option_line(line):
    """Parse a line with one or more options like 'A. text   B. text C. text'.

    Splits on option-letter markers that appear in increasing sequence
    (A→B→C→D), so options separated by even a single space are parsed
    correctly, while a stray 'X.' inside option text does not cause a false
    split (it would break the expected A/B/C/D order)."""
    line = line.strip()
    # Candidate markers: capital A-D + '.' + space, at line start or after space.
    markers = [(m.start(1), m.group(1))
               for m in re.finditer(r'(?:(?<=\s)|^)([A-D])\.(?=\s)', line)]
    if not markers:
        return []
    # Keep only markers forming an increasing run from the first one.
    seq, expected = [], markers[0][1]
    for pos, ltr in markers:
        if ltr == expected:
            seq.append((pos, ltr))
            expected = chr(ord(expected) + 1)
    opts = []
    for i, (pos, ltr) in enumerate(seq):
        end = seq[i + 1][0] if i + 1 < len(seq) else len(line)
        m = re.match(r'^[A-D]\.\s*(.+)', line[pos:end].strip())
        if m:
            opts.append((ltr, m.group(1).strip()))
    return opts


def parse_reading_questions(content):
    """Parse 阅读理解 习题 content into list of {num, text, opts} dicts."""
    questions = []
    lines = [l for l in content.split('\n')]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # Question line: starts with a number
        m = re.match(r'^(\d+)\.\s+(.+)', line)
        if m:
            num = m.group(1)
            q_text = m.group(2).strip()
            opts = []
            i += 1
            # Collect option lines until blank line or next question
            while i < len(lines):
                opt_line = lines[i]
                opt_stripped = opt_line.strip()
                if not opt_stripped:
                    i += 1
                    break
                if re.match(r'^\d+\.\s+', opt_stripped):
                    break
                parsed = parse_option_line(opt_stripped)
                opts.extend(parsed)
                i += 1
            questions.append({'num': num, 'text': q_text, 'opts': opts})
        else:
            i += 1
    return questions


ONE_ROW_THRESHOLD = 72  # total chars across all options to qualify for one-row layout


def options_fit_one_row(opts):
    """True if all option texts combined are short enough for a single row."""
    total = sum(len(ltr) + 2 + len(txt) for ltr, txt in opts)  # "A. text" per opt
    return total <= ONE_ROW_THRESHOLD


def render_reading_questions(name, content):
    """Render 阅读理解·习题 with adaptive option layout:
    - short options  → all in one row
    - long options   → each option on its own line
    """
    questions = parse_reading_questions(content)
    if not questions:
        return render_passage(name, content)  # fallback

    items = []
    for q in questions:
        q_html = (
            f'<div class="reading-q-text">'
            f'<span class="reading-q-num">{e(q["num"])}.</span>\u2002{e(q["text"])}'
            f'</div>'
        )
        opts = q['opts']
        if not opts:
            items.append(f'<div class="reading-question">{q_html}</div>')
            continue

        opt_cells = ''.join(
            f'<td class="reading-opt-cell">'
            f'<span class="reading-opt-letter">{e(ltr)}.</span>{e(txt)}'
            f'</td>'
            for ltr, txt in opts
        )

        if options_fit_one_row(opts):
            # All options in a single <tr>
            opts_html = (
                f'<table class="reading-opts-table one-row">'
                f'<tr>{opt_cells}</tr>'
                f'</table>'
            )
        else:
            # Each option on its own line via separate <tr> rows
            rows = ''.join(
                f'<tr><td class="reading-opt-cell">'
                f'<span class="reading-opt-letter">{e(ltr)}.</span>{e(txt)}'
                f'</td></tr>'
                for ltr, txt in opts
            )
            opts_html = f'<table class="reading-opts-table per-line">{rows}</table>'

        items.append(f'<div class="reading-question">{q_html}{opts_html}</div>')

    return f'<section class="section">{"".join(items)}</section>'


def process_mc_text(text):
    """Escape and convert ________ fill blanks to styled spans."""
    escaped = e(text)
    escaped = re.sub(r'_{4,}', r'<span class="mc-blank"></span>', escaped)
    return escaped


def parse_mc_questions(content):
    """Parse 单项选择 questions: (   )N. question + optional dialogue lines + option lines."""
    questions = []
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        m = re.match(r'^\(\s*\)\s*(\d+)\.\s+(.+)', line)
        if m:
            num = m.group(1)
            q_lines = [m.group(2).strip()]
            opts = []
            i += 1
            while i < len(lines):
                opt_stripped = lines[i].strip()
                if not opt_stripped:
                    i += 1
                    break
                if re.match(r'^\(\s*\)\s*\d+\.', opt_stripped):
                    break
                parsed = parse_option_line(opt_stripped)
                if parsed:
                    opts.extend(parsed)
                    i += 1
                else:
                    # Continuation of question (e.g. second dialogue line)
                    q_lines.append(opt_stripped)
                    i += 1
            questions.append({'num': num, 'lines': q_lines, 'opts': opts})
        else:
            i += 1
    return questions


def render_mc_questions(name, content):
    """Render 单项选择·习题.
    - Answer slot shown as ( ) text.
    - Short options (one-row): options appear inline after the question text on the same line.
    - Long options (per-line): options appear below the question text.
    """
    questions = parse_mc_questions(content)
    if not questions:
        return render_passage(name, content)

    SLOT = '(&nbsp;&nbsp;&nbsp;)'

    items = []
    for q in questions:
        text_html = '<br>'.join(process_mc_text(l) for l in q['lines'])
        opts = q['opts']

        # The body column (question text + options) is a flex child placed
        # after the slot and number, so the options align with the first
        # character of the question text — not under the ( ) / number.
        if not opts:
            body = f'<div class="mc-q-text">{text_html}</div>'
        elif options_fit_one_row(opts):
            # Short options: equal-width columns on one row below the stem.
            cells = ''.join(
                f'<td class="reading-opt-cell">'
                f'<span class="reading-opt-letter">{e(ltr)}.</span>{e(txt)}'
                f'</td>'
                for ltr, txt in opts
            )
            opts_html = (
                f'<table class="reading-opts-table one-row"><tr>{cells}</tr></table>'
            )
            body = f'<div class="mc-q-text">{text_html}</div>{opts_html}'
        else:
            rows = ''.join(
                f'<tr><td class="reading-opt-cell">'
                f'<span class="reading-opt-letter">{e(ltr)}.</span>{e(txt)}'
                f'</td></tr>'
                for ltr, txt in opts
            )
            opts_html = f'<table class="reading-opts-table per-line">{rows}</table>'
            body = f'<div class="mc-q-text">{text_html}</div>{opts_html}'

        q_html = (
            f'<div class="mc-q-header">'
            f'<span class="mc-answer-slot">{SLOT}</span>'
            f'<span class="mc-q-num">{e(q["num"])}.</span>'
            f'<div class="mc-q-body">{body}</div>'
            f'</div>'
        )
        items.append(f'<div class="mc-question">{q_html}</div>')

    return f'<section class="section">{"".join(items)}</section>'


def render_options(name, content):
    """Single-column boxed options — for 七选五."""
    items = []
    for line in content.split('\n'):
        line = line.strip()
        if not line: continue
        m = re.match(r'^([A-G])\.\s*(.+)', line)
        if m:
            items.append(
                f'<div class="option-item">'
                f'<span class="option-letter">{m.group(1)}.</span>'
                f'<span class="option-text">{e(m.group(2).strip())}</span>'
                f'</div>'
            )
    box = f'<div class="options-box">{"".join(items)}</div>'
    return f'<section class="section">{box}</section>'


def render_wordbank(name, content):
    """选词填空·词库: bank of selectable words in a bordered box.

    Preserves the row layout from the txt. Items within a row are separated by
    runs of 2+ spaces, so multi-word phrases (e.g. 'in danger') stay intact."""
    rows_html = []
    for line in content.split('\n'):
        if not line.strip():
            continue
        words = [w.strip() for w in re.split(r'\s{2,}', line.strip()) if w.strip()]
        cells = ''.join(f'<span class="wordbank-word">{e(w)}</span>' for w in words)
        rows_html.append(f'<div class="wordbank-row">{cells}</div>')
    if not rows_html:
        return ''
    return (
        f'<section class="section">'
        f'<div class="wordbank-box">{"".join(rows_html)}</div>'
        f'</section>'
    )


def render_vocab_practice(name, content):
    """Question-side: English words in 3-column grid with blank fill line.
    Extracts the English portion from lines that also have Chinese meanings."""
    words = []
    for l in content.split('\n'):
        l = l.strip()
        if not l or '[Leave empty' in l:
            continue
        words.append(extract_english_from_vocab_line(l))
    if not words:
        return ''
    items = ''.join(
        f'<div class="vocab-practice-item">'
        f'<span class="vocab-practice-word">{e(w)}</span>'
        f'<span class="vocab-practice-fill"></span>'
        f'</div>'
        for w in words
    )
    return (
        f'<section class="section">'
        f'<div class="section-label">写出下列单词的汉语意思：</div>'
        f'<div class="vocab-practice-grid">{items}</div>'
        f'</section>'
    )


def render_cloze_options(name, content):
    """完形填空 options: one grid row per question."""
    rows = []
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        num_m = re.match(r'^(\d+)\.\s+', line)
        if not num_m:
            continue
        num = num_m.group(1)
        rest = line[num_m.end():]
        parts = re.split(r'([A-D])\.\s*', rest)
        opts = []
        i = 1
        while i < len(parts) - 1:
            letter = parts[i]
            text = parts[i + 1].strip()
            opts.append((letter, text))
            i += 2
        if not opts:
            continue
        cells = ''.join(
            f'<td class="cloze-opt-cell"><span class="cloze-opt-label">{ltr}.</span>{e(opt)}</td>'
            for ltr, opt in opts
        )
        rows.append(f'<tr class="cloze-option-row"><td class="cloze-q-num">{num}.</td>{cells}</tr>')
    if not rows:
        return ''
    table = f'<table class="cloze-options-table">{"".join(rows)}</table>'
    return f'<section class="section">{table}</section>'


def extract_en_sentences(translation_content):
    """Return only English sentences (first line of each block)."""
    sentences, current = [], []
    for line in translation_content.split('\n'):
        if line.strip():
            current.append(line.strip())
        else:
            if current:
                sentences.append(current[0])
                current = []
    if current:
        sentences.append(current[0])

    def is_english(s):
        if not s:
            return False
        if '\u4e00' <= s[0] <= '\u9fa5':
            return False
        chinese = sum(1 for c in s if '\u4e00' <= c <= '\u9fa5')
        return chinese / len(s) < 0.4

    return [s for s in sentences if is_english(s)]


def render_translation_practice(section_name, sentences):
    """Question-side: section label + English sentence + blank line."""
    if not sentences:
        return ''
    items = []
    for sent in sentences:
        items.append(
            f'<div class="trans-practice-item">'
            f'<div class="trans-practice-en">{e(sent)}</div>'
            f'<div class="write-line"></div>'
            f'</div>'
        )
    return (
        f'<section class="section">'
        f'<div class="section-label">请写出下面这句话的翻译：</div>'
        f'{"".join(items)}'
        f'</section>'
    )


# ── Answer-Side Renderers ────────────────────────────────────────────────────

def split_answer_blocks(content):
    blocks, current = [], []
    for line in content.split('\n'):
        if re.match(r'^\d+[.\s]', line.strip()) and current:
            blocks.append('\n'.join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append('\n'.join(current))
    return [b.strip() for b in blocks if b.strip()]


def render_answer_block(block):
    lines = [l for l in block.split('\n') if l.strip()]
    if not lines:
        return ''

    first_line = lines[0].strip()
    extra_lines = [l.strip() for l in lines[1:] if l.strip()]

    if '【解析】' in first_line:
        header_raw, jiexi = first_line.split('【解析】', 1)
        jiexi = jiexi.strip()
    else:
        header_raw, jiexi = first_line, ''

    m = re.match(r'^(\d+)\.\s*(.*)', header_raw.strip())
    if not m or not m.group(2).strip():
        return f'<div class="answer-entry"><div class="generic-para">{e(block)}</div></div>'

    num, rest = m.group(1), m.group(2).strip()
    # The answer is English (a letter or a word/phrase); the optional 考查点/题型
    # note is Chinese. Split at the first CJK char so multi-word answers like
    # "to present" or "in danger" stay intact instead of being cut at a space.
    cjk = re.search(r'[一-龥]', rest)
    if cjk:
        answer, note = rest[:cjk.start()].strip(), rest[cjk.start():].strip()
    else:
        answer, note = rest, ''
    is_single_letter = (len(answer) == 1 and answer.isalpha() and answer.isupper())
    answer_class = 'answer-letter-big' if is_single_letter else 'answer-word'

    note_html = f'<span class="answer-note">{e(note)}</span>' if note else ''
    jiexi_html = f'<div class="answer-jiexi">{e(jiexi)}</div>' if jiexi else ''

    extra_parts = []
    for el in extra_lines:
        escaped = e(el)
        escaped = re.sub(r'【(.+?)】', r'<span class="tag-label">【\1】</span>', escaped)
        extra_parts.append(f'<div class="extra-line">{escaped}</div>')
    extra_html = f'<div class="answer-extra">{"".join(extra_parts)}</div>' if extra_parts else ''

    return (
        f'<div class="answer-entry">'
        f'<div class="answer-header">'
        f'<span class="answer-num">{num}.</span>'
        f'<span class="{answer_class}">{e(answer)}</span>'
        f'{note_html}'
        f'</div>'
        f'{jiexi_html}'
        f'{extra_html}'
        f'</div>'
    )


def render_answers(name, content):
    blocks = split_answer_blocks(content)
    entries_html = ''.join(render_answer_block(b) for b in blocks)
    return (
        f'<section class="section">'
        f'<div class="section-label">{e(name)}</div>'
        f'<div class="answers-container">{entries_html}</div>'
        f'</section>'
    )


def render_vocabulary(name, content):
    if not content or '[Leave empty' in content or not content.strip():
        return ''
    items = []
    for line in content.split('\n'):
        line = line.strip()
        if not line: continue
        m = re.match(r'^(\S+)\s*[-–]\s*(.+)', line)
        if m:
            items.append(
                f'<div class="vocab-item">'
                f'<span class="vocab-en">{e(m.group(1))}</span>'
                f'<span class="vocab-sep">—</span>'
                f'<span class="vocab-cn">{e(m.group(2).strip())}</span>'
                f'</div>'
            )
        else:
            items.append(f'<div class="vocab-item">{e(line)}</div>')
    if not items:
        return ''
    return (
        f'<section class="section">'
        f'<div class="section-label">{e(name)}</div>'
        f'<div class="vocab-grid">{"".join(items)}</div>'
        f'</section>'
    )


def render_translation_answers(name, content):
    """Answer-side: pair English + Chinese lines."""
    def is_chinese_line(s):
        return bool(s) and '\u4e00' <= s[0] <= '\u9fa5'

    lines = [l.strip() for l in content.split('\n') if l.strip()]
    entries_html = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not is_chinese_line(line):
            en_html = f'<div class="trans-en">{e(line)}</div>'
            cn_html = ''
            if i + 1 < len(lines) and is_chinese_line(lines[i + 1]):
                cn_html = f'<div class="trans-cn">{e(lines[i + 1])}</div>'
                i += 2
            else:
                i += 1
            entries_html.append(f'<div class="trans-block">{en_html}{cn_html}</div>')
        else:
            entries_html.append(f'<div class="trans-block"><div class="trans-cn">{e(line)}</div></div>')
            i += 1

    if not entries_html:
        return ''
    return (
        f'<section class="section">'
        f'<div class="section-label">{e(name)}</div>'
        f'{"".join(entries_html)}'
        f'</section>'
    )


# ── HTML Assembly ─────────────────────────────────────────────────────────────

def format_title(title):
    parts = title.split('_')
    if len(parts) >= 4:
        return parts[1], '  ·  '.join([parts[0]] + parts[2:])
    elif len(parts) >= 2:
        return parts[0], '  ·  '.join(parts[1:])
    return title, ''


ANSWER_DIVIDER = """\
<div class="answer-divider">
  <div class="answer-divider-line"></div>
  <div class="answer-divider-text">参 考 答 案</div>
  <div class="answer-divider-line"></div>
</div>"""


def generate_html(title, sections):
    display_title, display_subtitle = format_title(title)

    logo_html = ''
    if LOGO_PATH.exists():
        logo_html = f'<img src="file://{LOGO_PATH}" class="doc-logo" alt="">'

    subtitle_html = f'<div class="doc-subtitle">{e(display_subtitle)}</div>' if display_subtitle else ''
    header_html = (
        f'<div class="doc-header">'
        f'<div class="doc-header-row">'
        f'{logo_html}'
        f'<div class="doc-text">'
        f'<div class="doc-title">{e(display_title)}</div>'
        f'{subtitle_html}'
        f'</div>'
        f'</div>'
        f'</div>'
    )

    # Find translation section for practice rendering
    trans_section = next((s for s in sections if '·难句翻译' in s['name']), None)
    en_sentences = extract_en_sentences(trans_section['content']) if trans_section else []

    # Detect question type from first section name prefix
    qtype = sections[0]['name'].split('·')[0] if sections else ''

    # ── Question part ──────────────────────────────────────────────────────
    q_parts = [header_html]
    for section in sections:
        name, content = section['name'], section['content']
        if '·词库' in name:
            q_parts.append(render_wordbank(name, content))
        elif '·原文' in name:
            q_parts.append(render_passage(name, content))
        elif '·习题' in name:
            if qtype.startswith('阅读理解'):
                q_parts.append(render_reading_questions(name, content))
            elif qtype.startswith('单项选择'):
                q_parts.append(render_mc_questions(name, content))
            else:
                q_parts.append(render_passage(name, content))
        elif '·选项' in name:
            if qtype == '完形填空':
                q_parts.append(render_cloze_options(name, content))
            else:
                q_parts.append(render_options(name, content))
        elif '·重点词汇' in name:
            # Always show vocab practice on question side (English words only)
            q_parts.append(render_vocab_practice(name, content))
        # All other sections go to answer part

    # Append translation practice at end of question part
    if trans_section:
        practice = render_translation_practice(trans_section['name'], en_sentences)
        if practice:
            q_parts.append(practice)

    # ── Answer part ────────────────────────────────────────────────────────
    a_parts = [ANSWER_DIVIDER]
    for section in sections:
        name, content = section['name'], section['content']
        if '·答案解析' in name:
            a_parts.append(render_answers(name, content))
        elif '·重点词汇' in name and has_chinese_meanings(content):
            # Show full English–Chinese vocab on answer side
            a_parts.append(render_vocabulary(name, content))
        elif '·难句翻译' in name:
            a_parts.append(render_translation_answers(name + '答案', content))

    content = '\n'.join(q_parts + a_parts)
    return HTML_TEMPLATE.format(css=CSS, content=content)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_pdf_v5.py <input.txt> [output_dir]")
        sys.exit(1)

    input_path = Path(sys.argv[1]).resolve()
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    output_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else DEFAULT_OUTPUT
    output_dir.mkdir(parents=True, exist_ok=True)

    _, sections = parse_file(input_path)
    html_content = generate_html(input_path.stem, sections)

    stem = input_path.stem
    html_path = output_dir / f"{stem}.html"
    pdf_path = output_dir / f"{stem}.pdf"

    html_path.write_text(html_content, encoding='utf-8')
    print(f"HTML: {html_path}")

    pdf_js = find_pdf_js()
    result = subprocess.run(
        ['node', str(pdf_js), str(html_path), str(pdf_path)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"PDF: {pdf_path}")
    else:
        print(f"PDF conversion failed:\n{result.stderr}")
        sys.exit(1)


if __name__ == '__main__':
    main()
