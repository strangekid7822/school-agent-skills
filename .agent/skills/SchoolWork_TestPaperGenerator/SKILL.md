---
name: SchoolWork_TestPaperGenerator
description: Convert structured exam txt files (七选五, 语法填空, etc.) to beautifully formatted A4 PDFs. Black, grey and white design with typographic hierarchy.
---

# TestPaperGenerator Skill

Convert structured exam question txt files into beautifully formatted A4 PDFs.

## CRITICAL: You MUST Run the Existing Script — Never Write Code

**The script already exists. Do NOT write Python, HTML, or CSS under any circumstances.**

Your only job is to run this exact command:

```bash
python .agent/skills/SchoolWork_TestPaperGenerator/scripts/generate_pdf_v5.py "<input.txt>" [output_dir]
```

- Do NOT create a new script
- Do NOT modify the existing script
- Do NOT write inline HTML or CSS
- Do NOT use any other tool to generate the PDF
- If the script fails, report the error to the user — do not attempt to rewrite it

## Input

A structured `.txt` file with sections marked by `【...】` headers:

```
Title_line
========================================

【题型·词库】       ← word bank: rows of selectable words (选词填空)
【题型·原文】       ← passage with ___36___ blanks (完形填空/语法填空)
【题型·习题】       ← numbered questions + A/B/C/D options (阅读理解), or passage with ___N___ blanks (选词填空/语法填空)
【题型·选项】       ← A–G option list (七选五) or per-question ABCD (完形填空)
【题型·答案解析】   ← numbered answers with 【解析】
【题型·重点词汇】   ← word list: English-only OR "word - n. 中文" pairs
【题型·难句翻译】   ← English sentence + Chinese translation pairs
========================================
```

Supported question types: 七选五, 完形填空, 语法填空, 选词填空, 阅读理解, and any other format using the same structure.

## Output

- `{stem}.html` — intermediate HTML file
- `{stem}.pdf`  — final A4 PDF (no version suffix)

Both saved to `output_dir` (default: `/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/11_SkillWorkSpace`).

## Puppeteer

The script auto-detects and reuses the Puppeteer installation from `SchoolWork_WordTestGenerator/scripts/node_modules`. **Do NOT run `npm install`** — it is already available.

## Steps

1. Confirm the input file path with the user (or use the file they provide)
2. Run the script — **do not write any code**:
   ```bash
   python .agent/skills/SchoolWork_TestPaperGenerator/scripts/generate_pdf_v5.py "<input.txt>"
   ```
3. Report the output PDF path to the user

## Design (v5)

Two-part layout separated by a `━━ 参 考 答 案 ━━` divider with page break. Header always present: circular logo + bold title + grey subtitle (parsed from filename).

**Question part:**
- Header: logo + bold title + grey subtitle (always from filename stem)
- 选词填空·词库: rows of selectable words in a bordered box, shown above the passage; multi-word items (e.g. `in danger`) are kept intact (items split on 2+ spaces)
- Passage (原文): Georgia serif, `___36___` blanks, auto-detected passage title
- 阅读理解·习题: each question parsed individually — bold number + question text, then options in an **adaptive layout**: one row if all options are short (total chars across all options ≤ 72), otherwise one option per line
- Options (other types):
  - 七选五: single-column bordered box, no section label
  - 完形填空: grid table — one row per question (num | A | B | C | D), no box
- 重点词汇: section label reads `写出下列单词的汉语意思：` → 3-column italic word grid with fill lines; English words extracted from all vocab lines (even those with Chinese meanings)
- 难句翻译 practice: section label → `请写出下面这句话的翻译：` → English sentence (italic serif) → one blank writing line

**Answer part:**
- 答案解析: grey cards with left border; large bold letter (七选五/完形填空) or bold italic word (语法填空); grey 考查点; 解析 indented
- 重点词汇 (only if English–Chinese pairs exist): three-column compact grid
- 难句翻译答案: English sentence (italic) + Chinese answer (italic, underlined)

## Scripts

All scripts live in `scripts/`. Only the latest version is active — do not run older versions.

| File | Status | Notes |
|---|---|---|
| `scripts/generate_pdf_v5.py` | **Active (current)** | 阅读理解·习题 adaptive option layout (one-row / per-line); vocab practice for all word types |
| `scripts/html_to_pdf.js` | Support | Puppeteer HTML→PDF converter; called by Python script |
| `scripts/package.json` | Support | Node/Puppeteer manifest |

## Examples

Each question type has a reference HTML in `examples/`. Do not modify the examples.

| Question type | Reference HTML |
|---|---|
| 七选五 | `examples/example_七选五.html` |
| 完形填空 | `examples/example_完形填空.html` |
| 阅读理解 | `examples/example_阅读理解.html` |
| 选词填空 | `examples/example_选词填空.html` |

## Usage example

User: "帮我把这个文件生成PDF：2026_五年高考真题汇编_2025全国1卷_完形填空.txt"

→ Run: `python .agent/skills/SchoolWork_TestPaperGenerator/scripts/generate_pdf_v5.py "/path/to/2026_五年高考真题汇编_2025全国1卷_完形填空.txt"`
→ Output: `/path/to/2026_五年高考真题汇编_2025全国1卷_完形填空.pdf`
