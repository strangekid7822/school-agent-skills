---
name: SchoolWork_TestPaperGenerator_Danxuan
description: Combine multiple 单项选择 structured txt files into a single formatted A4 PDF with sequential global question numbering and per-试卷 section labels. No answers, vocabulary, or translations included.
---

# TestPaperGenerator_DanxiangxuanzeCombination

Combine any number of 单项选择 `.txt` files into one formatted A4 PDF. Questions are numbered globally across all papers; each paper is labelled 试卷 N.

## CRITICAL: Run the Script — Never Write Code

**The script already exists. Do NOT write Python, HTML, or CSS.**

Run this exact command:

```bash
python ".agent/skills/TestPaperGenerator_DanxiangxuanzeCombination/scripts/generate.py" \
    "file1.txt" "file2.txt" ... \
    --output OUTPUT_STEM \
    [--output-dir /path/to/dir] \
    [--title "自定义标题"] \
    [--start N]
```

- Do NOT create a new script
- Do NOT modify the existing script
- Do NOT write inline HTML or CSS
- If the script fails, report the error — do not attempt to rewrite it

## Input

One or more structured `.txt` files, each containing a `【单项选择·习题】` section:

```
试卷标题
========================================

【单项选择·习题】

(   )1. Question stem _________.
        A. option    B. option    C. option

(   )2. ...

【单项选择·答案解析】
...
========================================
```

Each file = one 试卷. Questions inside each file may be numbered from 1 — the script renumbers them globally.

## Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `inputs` | Yes | — | One or more `.txt` input files |
| `--output` | No | first file's stem | Output file stem (no extension) |
| `--output-dir` | No | directory of first input | Where to write `.html` and `.pdf` |
| `--title` | No | `英语单项选择综合卷` | Title shown in document header |
| `--start` | No | `1` | Starting 试卷 label index |

## Output

- `OUTPUT_STEM.html` — intermediate file
- `OUTPUT_STEM.pdf` — final A4 PDF

Both saved to `--output-dir` (default: same folder as first input file).

## Design

- Header: circular logo + bold title + grey subtitle (`中考模拟题库 · 试卷 1–N`)
- Per-paper section divider: small grey label `试卷 N`
- Questions: `( ) N.` prefix + question text (serif) + options in equal-width table columns
- Options: always on one row, equal-width columns (A/B/C or A/B/C/D)
- Global sequential numbering across all papers

## Puppeteer

Uses `SchoolWork_WordTestGenerator/scripts/node_modules` — **do NOT run `npm install`**.

## Steps

1. Confirm input `.txt` file paths with the user
2. Run the script — **do not write any code**
3. Report the output PDF path

## Examples

| File | Shows |
|---|---|
| `examples/example_单项选择综合卷.html` | 2-paper layout, 6 questions total |

## Usage examples

**Basic — combine 5 papers:**
```bash
python ".agent/skills/TestPaperGenerator_DanxiangxuanzeCombination/scripts/generate.py" \
    "试卷1_单项选择.txt" "试卷2_单项选择.txt" "试卷3_单项选择.txt" \
    "试卷4_单项选择.txt" "试卷5_单项选择.txt" \
    --output "英语单项选择综合卷_1-5"
```

**Append new papers (starting at 试卷 6):**
```bash
python ".agent/skills/TestPaperGenerator_DanxiangxuanzeCombination/scripts/generate.py" \
    "试卷6_单项选择.txt" "试卷7_单项选择.txt" \
    --output "英语单项选择_6-7" \
    --start 6
```

**Custom title:**
```bash
python ".agent/skills/TestPaperGenerator_DanxiangxuanzeCombination/scripts/generate.py" \
    "卷1.txt" "卷2.txt" \
    --output "期末单选综合" \
    --title "期末复习·单项选择专项"
```

User: "把这三个单选txt合并成一张综合卷PDF"

→ Run script with the three files as positional args, `--output` = reasonable stem derived from the files.
→ Report: `PDF saved: /path/to/output.pdf`
