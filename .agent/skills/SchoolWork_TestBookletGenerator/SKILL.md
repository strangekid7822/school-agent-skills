---
name: SchoolWork_TestBookletGenerator
description: Combine a FOLDER of per-school single-section exam papers (语法填空, 选词填空, 单项选择, 完形填空, 阅读理解, 七选五) into one A4 booklet PDF. Each paper is a labeled section with its original numbering; a compact, per-paper grouped answer key (answers only — no explanations, no vocabulary) goes in the back.
---

# TestBookletGenerator Skill

Turn a whole folder of structured exam papers — each a single section of the
**same type** — into one printable A4 **booklet** PDF.

Use this when the user has many per-school papers (e.g. 19 schools' 语法填空) and
wants them merged into a single practice booklet with answers in the back. For a
single paper, use `SchoolWork_TestPaperGenerator` instead.

## CRITICAL: Run the Existing Script — Never Write Code

The script already exists. Do **not** write Python/HTML/CSS, and do **not**
modify `generate_booklet.py` or the v5 script it reuses. Just run:

```bash
python .agent/skills/SchoolWork_TestBookletGenerator/scripts/generate_booklet.py \
  "<input_dir_or_combined_file>" "<output_dir>" --title "<booklet_stem>"
```

`<input_dir_or_combined_file>` may be a folder of single-paper `.txt` files OR
one combined multi-paper `.txt` file (see Input). `--title` is optional; if
omitted, the folder name (or combined file's stem) is used.

If the script fails, report the error — do not rewrite it.

## Input

Either of:

1. A **folder** of `.txt` files, each in the GaokaoPaperToTxt structured format
   (`【题型·原文】`, `【题型·习题】`, `【题型·选项】`, `【题型·答案解析】`, …). Files are
   combined in filename-sorted order.
2. A **single combined multi-paper `.txt` file** — several papers concatenated,
   each as `title + ==== + sections`. Papers are split on those per-paper
   boundaries; an optional document header (`收录范围：…` / `整理日期：…`) at the top
   is skipped automatically.

All papers should be the same section type. Each paper's first line is its title
(e.g. `2024_八年级下_期末_南岗区_英语_语法填空`), from which the per-paper label
(`2024 · 八年级下 · 期末 · 南岗区`) is derived.

Supported types: **语法填空, 选词填空, 单项选择, 完形填空, 阅读理解(A/B/C/D), 七选五.**

For **选词填空**, the per-paper `【选词填空·词库】` word bank is rendered as a bordered
box above each passage; multi-word bank items (e.g. `hang out`) stay intact.

## Output

Written to `output_dir`:
- `{title}.html` — intermediate
- `{title}.pdf`  — final A4 booklet

`--title` sets the file stem and the header (e.g. `8年级下_语法填空_哈尔滨` →
title `8年级下`, subtitle `语法填空 · 哈尔滨`). If omitted, the input folder name is used.

## What the booklet contains

**Question part** — for each paper, in order:
- A per-paper label heading (underlined).
- The paper's content rendered by section type (选词填空 word bank + passage with
  `___N___` blanks, 单项选择 questions, 完形填空 option grid, 阅读理解 questions,
  七选五 options), keeping the paper's **original numbering** (66–75, 96–105, …).

**`参 考 答 案` part** (page break):
- A **compact 5-column answer key**, grouped under each paper's label.
- **Answers only** — `【解析】` explanations, `重点词汇`, and `难句翻译` are dropped.
- Multi-word answers (e.g. `hang out`, `in danger`, `to present`) render in full.

## Robustness

- Sections are matched by **suffix** (`习题`/`原文`/`选项`/`答案解析`), so malformed
  source headers (e.g. the `语法填注` vs `语法填空` typo) do not leak vocab or
  explanations into the output.
- Papers with no parseable answers are reported as warnings on stdout.

## Puppeteer

Reuses the Puppeteer install under `SchoolWork_WordTestGenerator/scripts/node_modules`.
Do **not** run `npm install`.

## Relationship to other skills

- `SchoolWork_TestPaperGenerator` — single paper → PDF (reused internally here).
- `SchoolWork_TestPaperGenerator_Danxuan` — 单项选择-only booklet, no answers shown.
  This skill is the general, multi-type successor and additionally prints a
  compact answer key.

## Example

- `examples/example_语法填空_booklet.pdf` — 19 哈尔滨 八年级下 语法填空 papers merged.
- `examples/example_选词填空_booklet.pdf` — 5 哈尔滨 七年级下 选词填空 papers merged
  (word bank per paper, compact answer key with multi-word answers kept whole).
