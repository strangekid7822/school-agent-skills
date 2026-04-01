---
name: SchoolWork_WordTestGenerator
description: Generate vocabulary dictation test HTML and PDF files from word list txt files. Creates professional printable worksheets with two-column layout, plus answer keys.
---

# Word Test Generator Skill

Generate vocabulary dictation test HTML/PDF files and answer keys from word list files.

## CRITICAL: Run the Existing Script — Never Write HTML or Code

**The script already exists. Do NOT write HTML, CSS, or Python under any circumstances.**

Your only job is to run this command:

```bash
python .agent/skills/SchoolWork_WordTestGenerator/scripts/generate_word_test.py "<input.txt>" [output_dir] [--order random]
```

- Do NOT create new scripts
- Do NOT write inline HTML or CSS
- If the script fails, report the error — do not attempt to rewrite it

## Input

A vocabulary `.txt` file with numbered entries:
```
1.  word       /phonetic/   n.   Chinese meaning
2.  phrase                       Chinese meaning
```

## Options

- **Order**: omit for `正序` (original), add `--order random` for `乱序` (shuffled)

## Output (4 files total)

1. `{年级}_{单元}_单词默写_{正序|乱序}_{YYYY.MM.DD}.html` — blue theme, English column blank
2. `{年级}_{单元}_单词默写_{正序|乱序}_{YYYY.MM.DD}.pdf`
3. `{年级}_{单元}_单词默写_{正序|乱序}_{YYYY.MM.DD}_答案.html` — green theme, English filled
4. `{年级}_{单元}_单词默写_{正序|乱序}_{YYYY.MM.DD}_答案.pdf`

All saved to `output_dir` (default: same folder as input file).

## Puppeteer

The script auto-calls `html_to_pdf.js` internally for PDF generation. **Do NOT run `npm install`** — node_modules already exists.

## Steps

1. Confirm the input file path and output directory with the user
2. Run the script — **do not write any code**:
   ```bash
   python .agent/skills/SchoolWork_WordTestGenerator/scripts/generate_word_test.py "<input.txt>" "<output_dir>"
   ```
3. Report the 4 output file paths to the user

## File Locations

- Script:   `.agent/skills/SchoolWork_WordTestGenerator/scripts/generate_word_test.py`
- Template: `.agent/skills/SchoolWork_WordTestGenerator/resources/template.html`
- Logo:     `.agent/skills/SchoolWork_WordTestGenerator/resources/teacher_logo.jpg`

## Example Usage

User: "帮我用这个文件生成单词默写：9年级_词汇表_Unit2_2026.03.31.txt，输出到 9年级_单词默写/"

→ Run:
```bash
python .agent/skills/SchoolWork_WordTestGenerator/scripts/generate_word_test.py \
  "3_9年级/9年级_单词表/9年级_词汇表_Unit2_2026.03.31.txt" \
  "3_9年级/9年级_单词表/9年级_单词默写"
```
