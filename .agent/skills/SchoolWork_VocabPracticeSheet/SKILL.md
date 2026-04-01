---
name: SchoolWork_VocabPracticeSheet
description: Generate vocabulary memorization practice sheets (HTML/PDF) with 10-column layout for repeated writing practice. Landscape A4 optimized.
---

# Vocab Practice Sheet Generator

Generate vocabulary memorization practice sheets for students to write words repeatedly from memory.

## When to Use

- When user wants to create word memorization/practice sheets
- When user provides vocabulary lists (TXT, images, or screenshots)
- When user asks for "背诵练习", "单词练习", or "memorization worksheet"

## Input

- **TXT files**: Vocabulary lists in standard format (e.g., from WordListExtractor)
- **Images/Screenshots**: Pictures containing vocabulary words

## Pre-Execution (REQUIRED)

> [!IMPORTANT]
> **Before generating**, always ask the user:
> 1. "请问需要按字母顺序还是原始顺序排列？" (alphabetical or original order?)
> 2. Optional: Ask for 年级, 单元, 学生姓名 for filename

## Output

**Landscape A4 PDF** with 10-column layout:

| Col 1 | Col 2 | Cols 3-10 |
|-------|-------|-----------|
| English (black) | Chinese (gray) | Blank practice cells (alternating 英文/中文 headers) |

### File Naming
```
{年级}_{单元}_{学生姓名}_单词背诵练习_{原始顺序|字母顺序}_{YYYY.MM.DD}.pdf
```
- 年级, 单元, 学生姓名 are **optional**
- Examples:
  - `单词背诵练习_原始顺序_2026.02.03.pdf`
  - `7年级下_2单元_单词背诵练习_字母顺序_2026.02.03.pdf`
  - `7年级下_2单元_小明_单词背诵练习_原始顺序_2026.02.03.pdf`

### Output Directory

> [!IMPORTANT]
> **Always save output files to this directory:**
> ```
> /Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/.agent/workspace/pdf_extractor/output/
> ```

## One-Time Setup

Install Puppeteer for PDF generation:
```bash
cd .agent/skills/SchoolWork_VocabPracticeSheet/scripts
npm install puppeteer
```

## Steps

1. **Read input** - Parse TXT file or extract text from image
2. **Extract word pairs** - Get English word and Chinese meaning
3. **Apply ordering**:
   - 原始顺序: Keep original order
   - 字母顺序: Sort alphabetically by English word
4. **Copy logo to output directory** (REQUIRED before generating HTML):
   ```bash
   cp "/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/.agent/skills/SchoolWork_VocabPracticeSheet/resources/teacher_logo.jpg" "/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/.agent/workspace/pdf_extractor/output/"
   ```
5. **Generate HTML** in output directory using template from `resources/template.html`:
   - Replace `{{TITLE}}` with "单词背诵练习"
   - Replace `{{SUBTITLE}}` with grade/unit info (if provided)
   - Replace `{{TABLE_ROWS}}` with generated rows
6. **Generate PDF**:
   ```bash
   node "/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/.agent/skills/SchoolWork_VocabPracticeSheet/scripts/html_to_pdf.js" <output.html>
   ```

## Table Row Format

Each row has 10 columns (5 pairs of 英文/中文):
```html
<tr>
  <td class="col-en">{English}</td>
  <td class="col-zh">{Chinese}</td>
  <td class="col-practice-en"></td>
  <td class="col-practice-zh"></td>
  <td class="col-practice-en"></td>
  <td class="col-practice-zh"></td>
  <td class="col-practice-en"></td>
  <td class="col-practice-zh"></td>
  <td class="col-practice-en"></td>
  <td class="col-practice-zh"></td>
</tr>
```

## File Locations

- Template: `.agent/skills/SchoolWork_VocabPracticeSheet/resources/template.html`
- PDF Script: `.agent/skills/SchoolWork_VocabPracticeSheet/scripts/html_to_pdf.js`
- Logo: `.agent/skills/SchoolWork_VocabPracticeSheet/resources/teacher_logo.jpg`

## Example Usage

User: "帮我用这个词汇表生成背诵练习"
→ Ask: "请问需要按字母顺序还是原始顺序排列？"
→ User: "字母顺序"
→ Generate: `单词背诵练习_字母顺序_2026.02.03.pdf`
