---
name: SchoolWork_WordListExtractor_Simple
description: Extract vocabulary lists from textbook screenshots/images and convert them into a clean, structured TXT file. Outputs ONLY what is in the source image — no extra synonyms, word families, derivatives, or usage examples added.
---

# Word List Extractor — Simple (School Work)

This skill extracts vocabulary words **exactly as they appear** in textbook screenshots or images.
It is a **pure extraction** skill: do not add, enrich, or expand upon the source content in any way.

## When to Use This Skill

- When the user provides a screenshot or image of a vocabulary list from a textbook
- When the user wants a clean, faithful copy of exactly what is printed (no extras)
- Suitable for **all grade levels**: primary school (小学), middle school (初中), high school (高中)
- Use this skill instead of `SchoolWork_WordListExtractor` when no enrichment is needed

## When NOT to Use This Skill

- If the user wants synonyms, word families, or related phrases **added** → use `SchoolWork_WordListExtractor` instead

---

## Output Format

### File Header

```
[Grade] 词汇总表
整理日期：YYYY.MM.DD

说明：
- * 标注重点单词（课本加星号）
- 格式说明（供参考，更高年级适用）：
    基础格式：序号. (*) 单词  中文释义
    完整格式：序号. (*) 单词  /音标/  词性.  中文释义
    示例：1. *fox  /fɒks/  n.  狐狸
```

### Unit Separator

```
================================================================================
Unit X
================================================================================
```

### Word Entry Formats

Use the format that matches what is present in the source image:

**Format A — No phonetics or 词性 (e.g. primary school):**
```
1.  *word       中文释义
2.  word        中文释义
```

**Format B — With phonetics and 词性 (e.g. middle/high school):**
```
1.  *word  /音标/  词性.  中文释义
2.   word  /音标/  词性.  中文释义
```

**Format C — Mixed (some entries have phonetics, some don't):**
Apply Format B for entries that have phonetics/词性; Format A for those that don't.

---

## Extraction Rules

### ✅ ALWAYS Include

- Every word or phrase visible in the image, grouped by unit
- The `*` asterisk marker if the word has one in the source (marks key vocabulary 重点词汇)
- The full Chinese meaning exactly as printed (including all sense numbers, e.g. `（1）颜色 （2）为……着色`)
- Phonetic transcription `/音标/` if present in the source
- Part of speech (词性) if present in the source (e.g. `n.`, `v.`, `adj.`, `adv.`)
- Multi-word phrases and fixed expressions (e.g. `baby brother`, `by myself`, `Well done!`)
- Alternative forms shown in the source (e.g. `father (dad)`, `grandfather (grandpa)`)

### ❌ NEVER Add

- Synonyms or equivalent expressions not in the source
- Word families or derivatives not in the source
- Related phrases or usage examples not in the source
- Grammar notes or structural explanations
- Page numbers from the textbook (omit these)

---

## Formatting Details

- **Align columns** for readability (pad with spaces so Chinese meanings start at the same position within each unit)
- **Numbering**: sequential within each unit, restart at 1 for each new unit
- **`*` mark**: place immediately before the word, e.g. `*chair` not `* chair`
- **Multi-line definitions**: if a word's meaning spans two lines in the image, merge them into one line
- **Phrases**: list on their own numbered line, same as individual words

---

## Default Output Directory

Always save output files to:
```
/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/11_SkillWorkSpace/
```

---

## File Naming Convention

```
[Grade]_词汇表_[Scope]_[Date].txt
```

| Field | Examples |
|---|---|
| Grade | `小学3年级下`, `初中7年级下`, `高中必修1` |
| Scope | `全册` (all units), `Unit1`, `Unit3-4` |
| Date | `2026.03.17` |

**Full path examples:**
```
/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/11_SkillWorkSpace/小学3年级下_词汇表_全册_2026.03.17.txt
/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/11_SkillWorkSpace/初中7年级下_词汇表_Unit1_2026.03.17.txt
/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/11_SkillWorkSpace/高中必修1_词汇表_Unit3-4_2026.03.17.txt
```

---

## Processing Steps

1. **Examine the image(s)** — identify all units and all vocabulary entries
2. **Determine format** — check whether phonetics and/or 词性 are present in the source
3. **Extract each entry faithfully** — word (with `*` if marked), phonetics if present, 词性 if present, Chinese meaning
4. **Group by unit** — use the unit separator block
5. **Number sequentially** — restart numbering at 1 for each unit
6. **Align columns** — pad entries so meanings line up cleanly
7. **Write the file header** — include grade, date, and the format reference note
8. **Save the file** — use the naming convention above, save to the **Default Output Directory**: `/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/11_SkillWorkSpace/`

---

## Real Example File

A complete real-world example output is available in the skill folder:
```
.agent/skills/SchoolWork_WordListExtractor_Simple/examples/小学3年级下_词汇表_全册_2026.03.17.txt
```
This file was extracted from 小学三年级下 textbook screenshots (Units 1–6) and demonstrates the correct format for Format A (no phonetics/词性).

---

## Example Output

### Primary School (Format A — no phonetics/词性)

```
小学三年级下 词汇总表
整理日期：2026.03.17

说明：
- * 标注重点单词（课本加星号）
- 格式说明（供参考，更高年级适用）：
    基础格式：序号. (*) 单词  中文释义
    完整格式：序号. (*) 单词  /音标/  词性.  中文释义
    示例：1. *fox  /fɒks/  n.  狐狸

================================================================================
Unit 1
================================================================================

1.  *in          在……内；在……中
2.  *on          在……上（覆盖、附着）
3.  *under       在（或到、通过）……下面
4.  *box         盒；箱
5.  guess        猜测
6.  *many        许多
7.  *clean       打扫
8.  Well done!   做得好！
```

### Middle/High School (Format B — with phonetics and 词性)

```
初中七年级下 词汇总表
整理日期：2026.03.17

说明：
- * 标注重点单词（课本加星号）
- 格式说明（供参考，更高年级适用）：
    基础格式：序号. (*) 单词  中文释义
    完整格式：序号. (*) 单词  /音标/  词性.  中文释义
    示例：1. *fox  /fɒks/  n.  狐狸

================================================================================
Unit 1
================================================================================

1.  *fox       /fɒks/       n.   狐狸
2.  *run       /rʌn/        v.   跑；奔跑
3.  *beautiful /ˈbjuːtɪfl/  adj. 美丽的
4.  quickly    /ˈkwɪkli/    adv. 迅速地
```

---

## Continuous Improvement

> [!IMPORTANT]
> **After using this skill**, if you discover edge cases not covered here (e.g. a new source layout, unusual formatting in the image), **always ask the user** whether they would like to update this skill file.
>
> Examples of potential improvements:
> - New unit/section structures seen in the source
> - Entries with special formatting (e.g. numbered sub-senses)
> - New naming conventions needed for different grade systems
>
> **How to ask**: "I noticed [specific issue]. Would you like me to update the SchoolWork_WordListExtractor_Simple skill to handle this?"
