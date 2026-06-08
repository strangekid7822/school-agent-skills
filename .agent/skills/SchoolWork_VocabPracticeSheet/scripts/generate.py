#!/usr/bin/env python3
"""
Vocab Practice Sheet Generator
Usage: python3 generate.py <input.txt> <output_dir> [--alpha]
"""

import sys
import os
import re
import subprocess
from pathlib import Path

SKIP_PREFIXES = ('=', '初中', '高中', '整理', '说明', '-', 'Unit', '基础', '完整', '示例', '[', '来源', '日期')

def _extract_chinese(text):
    """Strip phonetics, POS tags, and non-Chinese parentheticals from a string."""
    text = re.sub(r'/[^/]+/', '', text)
    text = re.sub(r'\b(n|v|adj|adv|prep|conj|pron|num|art|interj)\.\s*', '', text)
    text = re.sub(r'[（(][^）)]*[）)]', lambda m: m.group(0) if re.search(r'[一-鿿]', m.group(0)) else '', text)
    # strip orphaned closing parenthetical at start (text extracted mid-parenthetical)
    # only strip if no opening paren precedes the closing one
    text = re.sub(r'^[^（(；]*[）)]\s*', '', text)
    text = re.sub(r'^[\s,，；;&]+|[\s,，；;&]+$', '', text)
    return text.strip()

def parse_vocab(txt_path):
    """Parse vocab TXT file, extracting English word and Chinese meaning."""
    words = []
    current_en = None
    current_zh = None

    def flush():
        if current_en and current_zh:
            words.append((current_en, current_zh))

    with open(txt_path, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if any(line.startswith(p) for p in SKIP_PREFIXES):
                continue

            # Tab-separated format
            if '\t' in line:
                flush()
                current_en = current_zh = None
                line = re.sub(r'^\d+\.\s*\*?', '', line)
                parts = line.split('\t', 1)
                en = re.sub(r'\s*/[^/]+/.*', '', parts[0]).strip()
                zh = _extract_chinese(parts[1].lstrip('\t'))
                if en and zh and re.match(r'^[a-zA-Z]', en):
                    words.append((en, zh))
                continue

            # Numbered entry line: "1.   word ..."
            m = re.match(r'^\d+\.\s+\*?(.+)', line)
            if m:
                flush()
                rest = m.group(1).strip()
                # English: everything before first phonetic /…/ or 2+ spaces
                en_m = re.match(r'^([a-zA-Z][a-zA-Z0-9\s\'\-\.]*?)(?=\s{2,}|/|$)', rest)
                current_en = en_m.group(1).strip() if en_m else None
                # Chinese: from first Chinese character to end of line
                zh_m = re.search(r'[一-鿿]', rest)
                current_zh = _extract_chinese(rest[zh_m.start():]) if zh_m else None
                continue

            # Continuation line (indented POS lines like "adj. 金色的")
            if current_en is not None:
                zh_m = re.search(r'[一-鿿]', line)
                if zh_m:
                    extra = _extract_chinese(line[zh_m.start():])
                    if extra:
                        current_zh = (current_zh + '；' + extra) if current_zh else extra

    flush()
    return words

def make_row(english, chinese):
    en_cls = 'col-en'
    if len(english) > 18:
        en_cls += ' very-long-text'
    elif len(english) > 12:
        en_cls += ' long-text'
    return f"""<tr>
  <td class="{en_cls}">{english}</td>
  <td class="col-zh">{chinese}</td>
  <td class="col-practice-en"></td>
  <td class="col-practice-zh"></td>
  <td class="col-practice-en"></td>
  <td class="col-practice-zh"></td>
  <td class="col-practice-en"></td>
  <td class="col-practice-zh"></td>
  <td class="col-practice-en"></td>
  <td class="col-practice-zh"></td>
</tr>"""

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate.py <input.txt> <output_dir> [--alpha]")
        sys.exit(1)

    input_txt = sys.argv[1]
    output_dir = Path(sys.argv[2])
    alpha = '--alpha' in sys.argv

    words = parse_vocab(input_txt)
    if alpha:
        words.sort(key=lambda x: x[0].lower())
        order_label = '字母顺序'
    else:
        order_label = '原始顺序'

    # Derive date from filename or use today
    stem = Path(input_txt).stem
    date_m = re.search(r'(\d{4}\.\d{2}\.\d{2})', stem)
    date_str = date_m.group(1) if date_m else '2026.04.11'

    # Grade from filename (supports 高一/高二/高三 and 初/高中 numeric grades like 8年级下)
    grade_m = re.search(r'\d+年级[上下]?|高[一二三]|初[一二三]', stem)
    grade = grade_m.group(0) if grade_m else '高一'

    # Unit from filename e.g. Unit7, Unit10
    unit_m = re.search(r'Unit\d+', stem, re.IGNORECASE)
    unit = unit_m.group(0) if unit_m else None

    title = "单词背诵练习"
    subtitle_parts = [grade]
    if unit:
        subtitle_parts.append(unit)
    subtitle_parts += [date_str, order_label, f"共{len(words)}词"]
    subtitle = ' · '.join(subtitle_parts)

    if unit:
        filename_base = f"{grade}_{unit}_单词背诵练习_{order_label}_{date_str}"
    else:
        filename_base = f"{grade}_单词背诵练习_{order_label}_{date_str}"

    rows_html = '\n'.join(make_row(en, zh) for en, zh in words)

    # Read template
    skill_dir = Path(__file__).parent.parent
    template_path = skill_dir / 'resources' / 'template.html'
    with open(template_path, encoding='utf-8') as f:
        html = f.read()

    html = html.replace('{{TITLE}}', title)
    html = html.replace('{{SUBTITLE}}', subtitle)
    html = html.replace('{{TABLE_ROWS}}', rows_html)

    # Copy logo to output dir
    logo_src = skill_dir / 'resources' / 'teacher_logo.jpg'
    logo_dst = output_dir / 'teacher_logo.jpg'
    if logo_src.exists() and not logo_dst.exists():
        import shutil
        shutil.copy(logo_src, logo_dst)

    html_out = output_dir / f"{filename_base}.html"
    pdf_out = output_dir / f"{filename_base}.pdf"

    with open(html_out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML written: {html_out}")

    # Generate PDF
    js_script = Path(__file__).parent / 'html_to_pdf.js'
    result = subprocess.run(['node', str(js_script), str(html_out), str(pdf_out)], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("PDF error:", result.stderr)
        sys.exit(1)

    # Remove temp HTML
    html_out.unlink()
    print(f"Done: {pdf_out}")

if __name__ == '__main__':
    main()
