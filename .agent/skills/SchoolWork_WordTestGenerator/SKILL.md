---
name: SchoolWork_WordTestGenerator
description: Generate vocabulary dictation test HTML and PDF files from word list knowledge point files. Creates professional printable worksheets with two-column table layout, plus answer keys.
---

# Word Test Generator Skill

Generate vocabulary dictation test HTML/PDF files and answer keys from word list files.

## Input

A knowledge point file (`.txt`) containing vocabulary words in format like:
```
1. word /phonetic/ n. Chinese meaning
   - related phrase
2. word /phonetic/ v. Chinese meaning
```

## Options

- **Order**: `正序` (original order) or `乱序` (shuffled). **Default: 正序**
- If user says "乱序", shuffle the words randomly before generating

## Output (4 files total)

1. Test HTML: `{年级}_{单元}_单词默写_{正序|乱序}_{YYYY.MM.DD}.html`
2. Test PDF: `{年级}_{单元}_单词默写_{正序|乱序}_{YYYY.MM.DD}.pdf`
3. Answer HTML: `{年级}_{单元}_单词默写_{正序|乱序}_{YYYY.MM.DD}_答案.html`
4. Answer PDF: `{年级}_{单元}_单词默写_{正序|乱序}_{YYYY.MM.DD}_答案.pdf`

Uses `teacher_logo.jpg` as logo (must be in output directory).

## One-Time Setup

Before first use, install Puppeteer for PDF generation:
```bash
cd .agent/skills/SchoolWork_WordTestGenerator/scripts
npm install puppeteer
```

## Steps

1. **Read the input file** provided by user
2. **Parse word entries** - Extract:
   - Number
   - English word/phrase
   - Chinese meaning
   - Part of speech (n./v./adj./adv./etc.)
   - Skip "Proper Names" section at end
   
3. **Apply ordering**:
   - 正序: Keep original order
   - 乱序: Shuffle words randomly

4. **Apply Color Scheme** (for visual distinction):
   - **正序 (Original Order) Test**: Blue theme
     - Header border: `#2563eb`, Title: `#1e3a5f`, Table header: `#1e3a5f`, Number column: `#2563eb` on `#f8fafc`
   - **乱序 (Random Order) Test**: Red theme
     - Header border: `#ef4444`, Title: `#7f1d1d`, Table header: `#7f1d1d`, Number column: `#ef4444` on `#fef2f2`
   - **All Answer Keys**: Green theme
     - Header border: `#10b981`, Title: `#064e3b`, Table header: `#064e3b`, Number column: `#10b981` on `#f0fdf4`, English text: `#059669`
    
5. **Generate TEST HTML** using template from `resources/template.html`:
   - Replace `{{TITLE}}` with "单词默写测验"
   - Replace `{{SUBTITLE}}` with grade/unit info (e.g., "7年级下册 · 2单元")
   - Replace `{{TOTAL}}` with word count
   - **Construct Table Rows**: Group words into pairs (Left word, Right word).
   - **Row Format (7 Columns)**:
     `<tr><td>#L</td><td>ZH</td><td></td><td class="spacer"></td><td>#R</td><td>ZH</td><td></td></tr>`
   - **English Column**: Must be **EMPTY** for test file.
   - **Alignment**: Ensure Left (#1) and Right (#2) are in the same `<tr>` for matched height.
   - Replace `{{TABLE_ROWS}}` in template with the generated rows string.

6. **Generate ANSWER HTML** using same template:
   - Use same word order as Test HTML.
   - **Row Format (7 Columns)**:
     `<tr><td>#L</td><td>ZH</td><td>EN_WORD</td><td class="spacer"></td><td>#R</td><td>ZH</td><td>EN_WORD</td></tr>`
   - **English Column Rules (CRITICAL)**:
     - Write **ONLY** the essential English word(s).
     - **REMOVE** all Part of Speech tags: `n.`, `v.`, `adj.`, `adv.`, `prep.`, `conj.`, `pron.`, `interj.`, `num.`, `art.`
     - **REMOVE** symbols like `&` at the end.
     - **REMOVE** phonetics `/.../` or `[...]`.
     - **Examples**:
       - `respect n. &` → `respect`
       - `shh (= sh) interj.` → `shh (= sh)` (Keep synonym if useful, remove interj.)
       - `hallway /'hɔ:lwei/` → `hallway`
       - `make ...` → `make ...`
       - `either/or` → `either/or`
       - `follow sb.` → `follow sb.`

7. **Save files** to same directory as input
8. **Copy Logo**:
   - Copy `teacher_logo.jpg` from `.agent/skills/SchoolWork_WordTestGenerator/resources/teacher_logo.jpg` to the output directory.
   - This ensures the HTML displays the logo correctly even if run in a new folder.
9. **Generate PDFs** by running for each HTML:
   ```bash
   node .agent/skills/SchoolWork_WordTestGenerator/scripts/html_to_pdf.js <output.html>
   ```

## File Locations

- Template: `.agent/skills/SchoolWork_WordTestGenerator/resources/template.html`
- PDF Script: `.agent/skills/SchoolWork_WordTestGenerator/scripts/html_to_pdf.js`

## Example Usage

User: "帮我用这个文件生成单词默写：7年级下_知识点_2单元_2026.01.16.txt"
→ Uses 正序 (default)

Output:
- `7年级下_2单元_单词默写_正序_2026.01.19.html` (English column empty)
- `7年级下_2单元_单词默写_正序_2026.01.19_答案.html` (English column filled, clean)
