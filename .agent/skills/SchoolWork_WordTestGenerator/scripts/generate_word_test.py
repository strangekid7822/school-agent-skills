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

SKILL_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE    = os.path.join(SKILL_DIR, 'resources', 'template.html')
LOGO_SRC    = os.path.join(SKILL_DIR, 'resources', 'teacher_logo.jpg')
PDF_SCRIPT  = os.path.join(SKILL_DIR, 'scripts', 'html_to_pdf.js')

# CSS injected before </style> to turn the template green for answer files
ANSWER_THEME = """
        /* Answer key — green theme */
        .header          { border-bottom-color: #10b981 !important; }
        .logo            { border-color: #10b981 !important; }
        h1               { color: #064e3b !important; }
        .main-table th   { background: #064e3b !important; }
        .col-num         { color: #10b981 !important; background: #f0fdf4 !important; }
        .col-en          { color: #059669 !important; }
        .main-table tr:last-child td:not(.col-spacer) { border-bottom-color: #064e3b !important; }
"""

POS_TAGS = ('n.', 'v.', 'adj.', 'adv.', 'prep.', 'conj.', 'pron.',
            'num.', 'art.', 'int.', 'interj.', 'inter.', 'pl.')


def clean_en(raw):
    """Strip phonetics, POS tags, and trailing & from an English fragment."""
    raw = re.sub(r'/[^/]*/', '', raw)      # /phonetics/
    raw = re.sub(r'\[[^\]]*\]', '', raw)   # [phonetics]
    raw = re.sub(r'\s*&\s*$', '', raw)     # trailing &
    return raw.strip()


def parse_entry(num, content):
    """Return dict with num, en_clean, zh_display for one numbered line."""
    # Find first Chinese character to split EN / ZH
    first_cn = next((i for i, c in enumerate(content)
                     if '\u4e00' <= c <= '\u9fa5'), -1)

    if first_cn == -1:
        # No Chinese — proper name or English-only entry
        return {'num': num, 'en_clean': clean_en(content), 'zh_display': ''}

    en_raw = content[:first_cn].strip()
    zh_raw = content[first_cn:].strip()

    # Pull trailing POS off the English fragment
    pos = ''
    # Handle compound "v. & n." / "n. & v." first
    m = re.search(r'([nv]\.\s*[&＆]\s*[nv]\.)\s*$', en_raw)
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
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('=') or line.startswith('-'):
                continue
            m = re.match(r'^(\d+)\.\s+(.*)', line)
            if m:
                words.append(parse_entry(m.group(1), m.group(2)))
    return words


def build_rows(words, mode):
    rows = []
    for i in range(0, len(words), 2):
        w1 = words[i]
        w2 = words[i + 1] if i + 1 < len(words) else None
        l_en = w1['en_clean'] if mode == 'answer' else ''
        r_num = w2['num']       if w2 else ''
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
    return '\n'.join(rows)


def render(template, subtitle, total, rows, is_answer):
    html = (template
            .replace('{{TITLE}}',      '单词默写测验')
            .replace('{{SUBTITLE}}',   subtitle)
            .replace('{{TOTAL}}',      str(total))
            .replace('{{TABLE_ROWS}}', rows))
    if is_answer:
        html = html.replace('</style>', ANSWER_THEME + '\n    </style>')
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
    parser.add_argument('output_dir', nargs='?', default=None,
                        help='Output directory (default: same as input file)')
    parser.add_argument('--order', choices=['original', 'random'], default='original')
    args = parser.parse_args()

    input_path = os.path.abspath(args.input_file)
    out_dir    = os.path.abspath(args.output_dir) if args.output_dir else os.path.dirname(input_path)
    os.makedirs(out_dir, exist_ok=True)

    fname = os.path.basename(input_path)

    # Parse grade and unit from filename
    # Supports: "9年级_词汇表_Unit2_..." and "7年级下_2单元_..."
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

    with open(TEMPLATE, encoding='utf-8') as f:
        template = f.read()

    # Copy logo to output directory
    logo_dest = os.path.join(out_dir, 'teacher_logo.jpg')
    if os.path.exists(LOGO_SRC) and not os.path.exists(logo_dest):
        shutil.copy2(LOGO_SRC, logo_dest)

    total = len(words)

    # --- Test ---
    test_path = os.path.join(out_dir, f"{base}.html")
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(render(template, subtitle, total, build_rows(words, 'test'), False))
    print(f"Test HTML  → {test_path}")
    to_pdf(test_path)

    # --- Answer ---
    ans_path = os.path.join(out_dir, f"{base}_答案.html")
    with open(ans_path, 'w', encoding='utf-8') as f:
        f.write(render(template, subtitle, total, build_rows(words, 'answer'), True))
    print(f"Answer HTML → {ans_path}")
    to_pdf(ans_path)

    print(f"\nDone — {total} words, {order_str}.")


if __name__ == '__main__':
    main()
