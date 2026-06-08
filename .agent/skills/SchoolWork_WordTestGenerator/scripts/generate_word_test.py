#!/usr/bin/env python3
"""
Word Test Generator
Usage: python generate_word_test.py <input.txt> [output_dir] [--order random]
"""

import os
import re
import sys
import random
import datetime
import shutil
import subprocess
import argparse

SKILL_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_SRC   = os.path.join(SKILL_DIR, 'resources', 'teacher_logo.jpg')
PDF_SCRIPT = os.path.join(SKILL_DIR, 'scripts', 'html_to_pdf.js')

TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>%%TITLE%%</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600&display=swap');
        @page { size: A4; margin: 12mm 12mm 5mm 12mm; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: "Noto Sans SC", "PingFang SC", sans-serif; font-size: 12pt; line-height: 1.4; background: #f5f5f5; padding: 20px; color: #333; }
        .page { max-width: 210mm; margin: 0 auto; background: #fff; padding: 25px 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { border-bottom: 3px solid %%BORDER_COLOR%%; padding-bottom: 15px; margin-bottom: 20px; }
        .title-row { display: flex; justify-content: space-between; align-items: center; }
        .title-group { display: flex; align-items: center; gap: 15px; }
        .logo { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid %%BORDER_COLOR%%; box-shadow: 0 2px 6px rgba(0,0,0,0.15); }
        h1 { font-size: 18pt; font-weight: 600; color: %%TITLE_COLOR%%; letter-spacing: 1px; }
        .subtitle { font-size: 11pt; color: #64748b; margin-top: 4px; }
        .info-box { display: flex; gap: 25px; font-size: 11pt; color: #475569; }
        .info-box .field { display: flex; align-items: baseline; gap: 8px; }
        .info-box .underline { display: inline-block; width: 70px; border-bottom: 1px solid #333; vertical-align: bottom; margin-bottom: 2px; }
        .info-box .underline.short { width: 40px; }
        .main-table { width: 100%; border-collapse: collapse; font-size: 11pt; }
        .main-table th { background: %%HEADER_BG%%; color: #fff; font-weight: 500; padding: 8px 10px; text-align: left; font-size: 10pt; letter-spacing: 0.5px; }
        .main-table td { padding: 8px 10px; border-bottom: 1px solid #e5e7eb; vertical-align: middle; }
        .col-num { width: 30px; text-align: center; font-weight: 600; color: %%NUM_COLOR%%; background: %%NUM_BG%%; }
        .col-zh { width: 30%; }
        .col-en { width: 20%; background: #fafafa; %%EN_COLOR_RULE%% }
        .col-spacer { width: 10mm; border: none !important; background: transparent !important; }
        .main-table tr:last-child td:not(.col-spacer) { border-bottom: 2px solid %%HEADER_BG%%; }
        @media print {
            body { background: #fff; padding: 0; }
            .page { box-shadow: none; padding: 0; padding-top: 5mm; }
            tr { page-break-inside: avoid; }
            table { page-break-inside: avoid; }
            .header { page-break-inside: avoid; page-break-after: avoid; }
            thead { display: table-header-group; }
        }
    </style>
</head>
<body>
    <div class="page">
        <div class="header">
            <div class="title-row">
                <div class="title-group">
                    <img src="teacher_logo.jpg" alt="Teacher" class="logo">
                    <div>
                        <h1>%%TITLE%%</h1>
                        <div class="subtitle">%%SUBTITLE%%</div>
                    </div>
                </div>
                <div class="info-box">
                    <div class="field">姓名 <span class="underline"></span></div>
                    <div class="field">班级 <span class="underline"></span></div>
                    <div class="field">得分 <span class="underline short"></span>/%%TOTAL%%</div>
                </div>
            </div>
        </div>
        <table class="main-table">
            <thead>
                <tr>
                    <th class="col-num">#</th>
                    <th class="col-zh">中文</th>
                    <th class="col-en">英文</th>
                    <th class="col-spacer"></th>
                    <th class="col-num">#</th>
                    <th class="col-zh">中文</th>
                    <th class="col-en">英文</th>
                </tr>
            </thead>
            <tbody>
                %%TABLE_ROWS%%
            </tbody>
        </table>
    </div>
</body>
</html>"""

# Blue theme (test)
BLUE = dict(
    BORDER_COLOR='#2563eb',
    TITLE_COLOR='#1e3a5f',
    HEADER_BG='#1e3a5f',
    NUM_COLOR='#2563eb',
    NUM_BG='#f8fafc',
    EN_COLOR_RULE='',
)

# Green theme (answer)
GREEN = dict(
    BORDER_COLOR='#10b981',
    TITLE_COLOR='#064e3b',
    HEADER_BG='#064e3b',
    NUM_COLOR='#10b981',
    NUM_BG='#f0fdf4',
    EN_COLOR_RULE='color: #059669;',
)

# Ordered longest-first so "pron." is checked before "n.", "adv." before "v.", etc.
POS_TAGS = sorted(
    ['n.', 'v.', 'adj.', 'adv.', 'prep.', 'conj.', 'pron.',
     'num.', 'art.', 'int.', 'interj.', 'inter.', 'pl.'],
    key=len, reverse=True
)


def clean_en(raw):
    """Strip phonetics, POS tags, verb forms in parens, trailing &, extra spaces."""
    # Remove phonetics /.../ and [...]
    raw = re.sub(r'/[^/]*/', '', raw)
    raw = re.sub(r'\[[^\]]*\]', '', raw)
    # Remove trailing &
    raw = re.sub(r'\s*&\s*$', '', raw)
    # Collapse multiple spaces into one
    raw = re.sub(r'\s{2,}', ' ', raw)
    return raw.strip()


def parse_entry(num, content):
    """Return dict with num, en_clean, zh_display for one numbered line."""
    # Strip leading * (marks important/bold words in source)
    content = content.lstrip('*').lstrip()
    # Find first Chinese character (or Chinese punctuation like 《（) to split EN / ZH
    first_cn = next((i for i, c in enumerate(content)
                     if '\u4e00' <= c <= '\u9fa5' or c in '《（'), -1)

    # Backtrack to include digits immediately before first Chinese char
    # e.g. "n.  13至19岁" — the "13" belongs to the Chinese meaning
    while first_cn > 0 and content[first_cn - 1].isdigit():
        first_cn -= 1

    # Backtrack past ASCII '(' that opens a Chinese parenthetical
    # e.g. "n.  (鱼) 鳍" — the "(" belongs to the Chinese meaning
    if first_cn > 0 and content[first_cn - 1] == '(':
        first_cn -= 1

    if first_cn == -1:
        # No Chinese — proper name or English-only entry
        return {'num': num, 'en_clean': clean_en(content), 'zh_display': ''}

    en_raw = content[:first_cn].strip()
    zh_raw = content[first_cn:].strip()

    # Strip trailing parenthetical content FIRST (before POS check),
    # because POS may sit before parens: "v. (rang/ræŋ/，rung/rʌŋ/)"
    # Remove all trailing (...) groups that contain no Chinese characters.
    while True:
        m2 = re.search(r'\s*\([^)]*\)\s*$', en_raw)
        if m2 and not any('\u4e00' <= c <= '\u9fa5' for c in m2.group()):
            en_raw = en_raw[:m2.start()].strip()
        else:
            break

    # Pull trailing POS off the English fragment.
    # Match full POS block: units joined by ", " or " & " e.g. "prep., adv. & conj."
    pos = ''
    _pos_unit = r'(?:adj|adv|prep|conj|pron|interj|inter|num|art|int|pl|[nv])\.'
    _pos_block = rf'(?:{_pos_unit}(?:\s*[,，]\s*|\s*[&＆]\s*))*{_pos_unit}'
    m = re.search(rf'({_pos_block})\s*$', en_raw)
    if m:
        pos = m.group(1)
        en_raw = en_raw[:m.start()].strip()
    else:
        for tag in POS_TAGS:
            if en_raw.endswith(tag):
                pos = tag
                en_raw = en_raw[:-len(tag)].strip()
                break

    zh_display = f"{pos} {zh_raw}".strip() if pos else zh_raw
    return {'num': num, 'en_clean': clean_en(en_raw), 'zh_display': zh_display}


def parse_file(filepath):
    words = []
    entry_num = 0  # track current numbered entry for sub-items
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith('=') or stripped.startswith('-'):
                continue
            # Stop at proper noun section (地名/人名)
            if '地名' in stripped or '人名' in stripped:
                break
            # Match numbered entry (with or without space after dot)
            m = re.match(r'^(\d+)\.\s*(.*)', stripped)
            if m:
                entry_num += 1
                words.append(parse_entry(str(entry_num), m.group(2)))
            elif line.startswith((' ', '\t')) and stripped:
                # Indented sub-item — treat as its own vocab entry
                entry_num += 1
                words.append(parse_entry(str(entry_num), stripped))
    return words


def build_rows(words, mode):
    rows = []
    for i in range(0, len(words), 2):
        w1 = words[i]
        w2 = words[i + 1] if i + 1 < len(words) else None
        l_en = w1['en_clean'] if mode == 'answer' else ''
        r_num = w2['num']        if w2 else ''
        r_zh  = w2['zh_display'] if w2 else ''
        r_en  = (w2['en_clean'] if mode == 'answer' else '') if w2 else ''
        rows.append(
            f'<tr>'
            f'<td class="col-num">{w1["num"]}</td>'
            f'<td class="col-zh">{w1["zh_display"]}</td>'
            f'<td class="col-en">{l_en}</td>'
            f'<td class="col-spacer"></td>'
            f'<td class="col-num">{r_num}</td>'
            f'<td class="col-zh">{r_zh}</td>'
            f'<td class="col-en">{r_en}</td>'
            f'</tr>'
        )
    return '\n                '.join(rows)


def render(subtitle, total, rows, theme, title):
    html = TEMPLATE
    for key, val in theme.items():
        html = html.replace('%%' + key + '%%', val)
    html = (html
            .replace('%%TITLE%%',      title)
            .replace('%%SUBTITLE%%',   subtitle)
            .replace('%%TOTAL%%',      str(total))
            .replace('%%TABLE_ROWS%%', rows))
    return html


def to_pdf(html_path):
    node = shutil.which('node') or 'node'
    r = subprocess.run([node, PDF_SCRIPT, html_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  PDF warning: {r.stderr.strip()}", file=sys.stderr)
    else:
        print(f"  {r.stdout.strip()}")


def main():
    parser = argparse.ArgumentParser(description='Generate word dictation test HTML + PDF')
    parser.add_argument('input_file')
    parser.add_argument('output_dir', nargs='?', default=None)
    parser.add_argument('--order', choices=['original', 'random'], default='original')
    args = parser.parse_args()

    input_path = os.path.abspath(args.input_file)
    out_dir    = os.path.abspath(args.output_dir) if args.output_dir else os.path.dirname(input_path)
    os.makedirs(out_dir, exist_ok=True)

    fname = os.path.basename(input_path)
    g = re.search(r'(\d+年级[上下]?)', fname)
    u = re.search(r'(Unit\d+|\d+单元)', fname, re.IGNORECASE)
    grade    = g.group(1) if g else ''
    unit     = u.group(1) if u else ''
    subtitle = f"{grade} · {unit}" if (grade and unit) else os.path.splitext(fname)[0]

    words = parse_file(input_path)
    if not words:
        print("No words parsed — check input file format.", file=sys.stderr)
        sys.exit(1)

    if args.order == 'random':
        random.shuffle(words)
        for i, w in enumerate(words):
            w['num'] = str(i + 1)

    order_str = '乱序' if args.order == 'random' else '正序'
    today     = datetime.datetime.now().strftime('%Y.%m.%d')
    base      = f"{grade}_{unit}_单词默写_{order_str}_{today}"

    # Copy logo to output directory
    logo_dest = os.path.join(out_dir, 'teacher_logo.jpg')
    if os.path.exists(LOGO_SRC) and not os.path.exists(logo_dest):
        shutil.copy2(LOGO_SRC, logo_dest)

    total = len(words)

    # Test
    test_path = os.path.join(out_dir, f"{base}.html")
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(render(subtitle, total, build_rows(words, 'test'), BLUE, '单词默写测验'))
    print(f"Test HTML  → {test_path}")
    to_pdf(test_path)

    # Answer
    ans_path = os.path.join(out_dir, f"{base}_答案.html")
    with open(ans_path, 'w', encoding='utf-8') as f:
        f.write(render(subtitle, total, build_rows(words, 'answer'), GREEN, '单词默写测验'))
    print(f"Answer HTML → {ans_path}")
    to_pdf(ans_path)

    print(f"\nDone — {total} words, {order_str}.")


if __name__ == '__main__':
    main()
