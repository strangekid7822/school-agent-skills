#!/usr/bin/env python3
"""
TestBookletGenerator

Combine a FOLDER of per-school single-section exam papers (each in the
GaokaoPaperToTxt structured format) into ONE A4 booklet PDF:

  - Question part: every paper rendered in sequence, each under its own
    per-paper label, keeping the paper's ORIGINAL blank/question numbering.
  - 参 考 答 案 part: a COMPACT multi-column answer key, grouped per paper.
    Answers only — no 【解析】 explanations, no 重点词汇, no 难句翻译.

Supports the same section types as TestPaperGenerator:
  语法填空, 单项选择, 完形填空, 阅读理解(A/B/C/D), 七选五.

Robust to malformed source headers (e.g. the 语法填注 vs 语法填空 typo): sections
are matched by their suffix (习题/原文/选项/答案解析), not exact equality.

Input may be EITHER a folder of single-paper .txt files OR one combined
multi-paper .txt file (papers split on per-paper title + ==== boundaries).

Usage:
  python generate_booklet.py <input_dir_or_file> <output_dir> --title "8年级下_语法填空_哈尔滨"
  python generate_booklet.py <input_dir_or_file> <output_dir>   # title inferred

The script REUSES the rendering helpers from the sibling TestPaperGenerator
skill (generate_pdf_v5.py); it does not fork or modify them.
"""

import sys
import re
import html as html_module
import argparse
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
SKILL_DIR = SCRIPTS_DIR.parent
V5_SCRIPTS = SKILL_DIR.parent / "SchoolWork_TestPaperGenerator" / "scripts"

# Reuse the tested renderers + CSS from TestPaperGenerator v5.
sys.path.insert(0, str(V5_SCRIPTS))
import generate_pdf_v5 as v5  # noqa: E402

# Section-type tokens stripped from filenames when deriving a paper label.
SECTION_WORDS = [
    '语法填空', '语法填注', '选词填空', '单项选择', '完形填空', '七选五',
    '任务型阅读', '补全对话', '阅读理解',
]

# ── Extra CSS layered on top of the v5 stylesheet ────────────────────────────
EXTRA_CSS = """
/* ── Per-paper label (booklet) ── */
.paper-label {
    font-size: 8.5pt;
    font-weight: 800;
    letter-spacing: 0.14em;
    color: #111;
    border-bottom: 1px solid #ddd;
    padding-bottom: 4px;
    margin: 16px 0 10px;
    page-break-after: avoid;
}
.paper-label:first-of-type { margin-top: 0; }

/* ── Compact grouped answer key ── */
.ans-group { margin-bottom: 11px; page-break-inside: avoid; }
.ans-group-label {
    font-size: 7pt;
    font-weight: 700;
    letter-spacing: 0.18em;
    color: #999;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4px;
    margin-bottom: 7px;
    text-transform: uppercase;
}
.answers-compact {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 2px 16px;
}
.ans-item {
    font-size: 9.5pt;
    padding: 2px 0;
    border-bottom: 1px solid #f0f0f0;
    line-height: 1.5;
}
.ans-num { color: #aaa; font-weight: 700; font-size: 8pt; margin-right: 5px; }
.ans-word { font-weight: 700; font-style: italic; color: #111; }
.ans-note { color: #999; font-size: 7.5pt; margin-left: 4px; font-style: normal; }
"""


def e(text):
    return html_module.escape(str(text))


def label_from_title(title):
    """'2024_八年级下_期末_南岗区_英语_语法填空' -> '2024 · 八年级下 · 期末 · 南岗区'."""
    parts = []
    for p in title.split('_'):
        if p == '英语':
            continue
        if any(p.startswith(w) for w in SECTION_WORDS):
            continue
        parts.append(p)
    return ' · '.join(parts) if parts else title


def split_sections(lines):
    """Split a file's lines on any 【...】 header. Returns [(name, content_str)]."""
    secs, name, buf = [], None, []
    for l in lines:
        m = re.match(r'^【(.+?)】\s*$', l.strip())
        if m:
            if name is not None:
                secs.append((name, '\n'.join(buf).strip()))
            name, buf = m.group(1), []
        elif name is not None:
            buf.append(l)
    if name is not None:
        secs.append((name, '\n'.join(buf).strip()))
    return secs


def _is_divider(s):
    s = s.strip()
    return bool(s) and set(s) == {'='}


def split_combined(lines):
    """Split a SINGLE combined multi-paper file into per-paper line blocks.

    Each paper starts with a title line immediately followed by a ==== divider.
    An optional document header (… 收录范围：… / 整理日期：… ====) at the top is
    skipped: it is recognised by a full-width colon on the line above its divider.
    Returns a list of line-lists, one per paper (title/divider/blanks trimmed of
    any trailing divider so they don't leak into a section)."""
    # Skip an optional document header: everything up to & incl. its divider.
    start = 0
    for i, l in enumerate(lines):
        if _is_divider(l):
            prev = lines[i - 1].strip() if i > 0 else ''
            prev2 = lines[i - 2].strip() if i > 1 else ''
            if '：' in prev or '：' in prev2:  # meta lines like 收录范围：/整理日期：
                start = i + 1
            break
    body = lines[start:]

    # Paper starts: a non-blank, non-【, non-divider line followed by a divider.
    starts = []
    for i in range(len(body) - 1):
        cur = body[i].strip()
        if not cur or cur.startswith('【') or _is_divider(cur):
            continue
        if _is_divider(body[i + 1]):
            starts.append(i)
    if not starts:
        return [body]

    blocks = []
    for k, s in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(body)
        block = body[s:end]
        while block and (not block[-1].strip() or _is_divider(block[-1])):
            block.pop()  # trim trailing blanks / closing divider
        blocks.append(block)
    return blocks


def parse_paper_lines(lines, fallback_title=''):
    """Return dict {label, qtype, sections:[(name,content)], answers:[(num,ans,note)]}."""
    title = next((l.strip() for l in lines if l.strip() and not l.strip().startswith('=')), fallback_title)
    secs = split_sections(lines)

    qtype = ''
    for name, _ in secs:
        if name.endswith('习题') or name.endswith('原文'):
            qtype = name.split('·')[0]
            break

    answers = []
    for name, content in secs:
        if name.endswith('答案解析'):
            for line in content.split('\n'):
                line = re.split(r'【解析】', line.strip())[0].strip()
                # Answers are always English; drop any inline Chinese annotation
                # (e.g. 考查点 labels like "考查非谓语动词" some papers put before 【解析】).
                cjk = re.search(r'[一-鿿]', line)
                if cjk:
                    line = line[:cjk.start()].strip()
                # After the Chinese 考查点 is stripped, the remainder is the full
                # English answer — keep it whole so multi-word answers like
                # "in danger" / "hang out" / "to present" don't get split.
                m = re.match(r'^(\d+)\.\s*(.+)$', line)
                if m:
                    answers.append((m.group(1), m.group(2).strip(), ''))
    return {'label': label_from_title(title), 'qtype': qtype, 'sections': secs, 'answers': answers}


def parse_paper(path):
    """Parse one single-paper .txt file (folder-input mode)."""
    return parse_paper_lines(path.read_text(encoding='utf-8').splitlines(), fallback_title=path.stem)


def render_question_side(paper):
    """Render one paper's question content using the v5 renderers, by section type."""
    qtype = paper['qtype']
    parts = [f'<div class="paper-label">{e(paper["label"])}</div>']
    for name, content in paper['sections']:
        if name.endswith('词库'):  # 选词填空 word bank, shown above the passage
            parts.append(v5.render_wordbank(name, content))
        elif name.endswith('原文'):
            parts.append(v5.render_passage(name, content))
        elif name.endswith('习题'):
            if qtype.startswith('阅读理解'):
                parts.append(v5.render_reading_questions(name, content))
            elif qtype.startswith('单项选择'):
                parts.append(v5.render_mc_questions(name, content))
            else:  # 语法填空 and any passage-with-blanks type
                parts.append(v5.render_passage(name, content))
        elif name.endswith('选项'):
            if qtype.startswith('完形填空'):
                parts.append(v5.render_cloze_options(name, content))
            else:  # 七选五
                parts.append(v5.render_options(name, content))
        # 答案解析 / 重点词汇 / 难句翻译 intentionally skipped on the question side
    return ''.join(parts)


def render_answer_group(paper):
    if not paper['answers']:
        return ''
    items = []
    for num, ans, note in paper['answers']:
        note_html = f'<span class="ans-note">{e(note)}</span>' if note else ''
        items.append(
            f'<div class="ans-item"><span class="ans-num">{e(num)}.</span>'
            f'<span class="ans-word">{e(ans)}</span>{note_html}</div>'
        )
    return (
        f'<div class="ans-group">'
        f'<div class="ans-group-label">{e(paper["label"])}</div>'
        f'<div class="answers-compact">{"".join(items)}</div>'
        f'</div>'
    )


def build_html(booklet_title, papers):
    display_title, display_subtitle = v5.format_title(booklet_title)

    logo_html = ''
    if v5.LOGO_PATH.exists():
        logo_html = f'<img src="file://{v5.LOGO_PATH}" class="doc-logo" alt="">'
    subtitle_html = f'<div class="doc-subtitle">{e(display_subtitle)}</div>' if display_subtitle else ''
    header = (
        f'<div class="doc-header"><div class="doc-header-row">{logo_html}'
        f'<div class="doc-text"><div class="doc-title">{e(display_title)}</div>'
        f'{subtitle_html}</div></div></div>'
    )

    q_html = ''.join(render_question_side(p) for p in papers)
    a_html = ''.join(render_answer_group(p) for p in papers)

    content = header + q_html + v5.ANSWER_DIVIDER + a_html
    css = v5.CSS + EXTRA_CSS
    return v5.HTML_TEMPLATE.format(css=css, content=content)


def main():
    ap = argparse.ArgumentParser(description="Combine per-school papers into one booklet PDF.")
    ap.add_argument('input_dir', help="Folder of structured .txt papers, OR a single combined multi-paper .txt file.")
    ap.add_argument('output_dir', help="Where to write {title}.html and {title}.pdf.")
    ap.add_argument('--title', help="Booklet stem, e.g. 8年级下_语法填空_哈尔滨. Inferred if omitted.")
    args = ap.parse_args()

    in_path = Path(args.input_dir).resolve()
    if in_path.is_dir():
        files = sorted(p for p in in_path.glob('*.txt'))
        if not files:
            print(f"Error: no .txt files in {in_path}")
            sys.exit(1)
        papers = [parse_paper(f) for f in files]
        sources = [f.name for f in files]
        default_title = in_path.name
    else:
        if not in_path.exists():
            print(f"Error: input not found: {in_path}")
            sys.exit(1)
        # Single combined multi-paper file: split into per-paper blocks.
        blocks = split_combined(in_path.read_text(encoding='utf-8').splitlines())
        papers = [parse_paper_lines(b) for b in blocks]
        sources = [p['label'] for p in papers]
        default_title = in_path.stem
        print(f"Combined file: split into {len(papers)} papers")

    # Warn about papers with no detected answers (helps catch malformed inputs).
    for name, p in zip(sources, papers):
        if not p['answers']:
            print(f"Warning: no answers parsed from {name}")

    title = args.title or default_title
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    html_path = out_dir / f"{title}.html"
    pdf_path = out_dir / f"{title}.pdf"
    html_path.write_text(build_html(title, papers), encoding='utf-8')
    print(f"HTML: {html_path}")
    print(f"Papers: {len(papers)} | type: {papers[0]['qtype'] or 'unknown'}")

    pdf_js = v5.find_pdf_js()
    result = subprocess.run(['node', str(pdf_js), str(html_path), str(pdf_path)],
                            capture_output=True, text=True)
    if result.returncode == 0:
        print(f"PDF: {pdf_path}")
    else:
        print(f"PDF conversion failed:\n{result.stderr}")
        sys.exit(1)


if __name__ == '__main__':
    main()
