---
name: SchoolWork_WordTest_AnyNumber_Generator
description: Extract words from any vocabulary TXT file, randomly pick any number of them (10, 20, 30, 40, or any N), and output a clean, numbered, dated word list TXT file ready for dictation practice.
---

# Word Test AnyNumber Generator Skill

Randomly select N words from a structured vocabulary file and write a dated test-word list.

## ⚠️ IMPORTANT: Use the Existing Script

**DO NOT write a new Python script.** A permanent script already exists at:

```
.agent/skills/SchoolWork_WordTest_AnyNumber_Generator/scripts/pick_words.py
```

Always call this script directly via the terminal. Never recreate it.

---

## Input

A vocabulary `.txt` file with numbered entries in any of these formats:

```
1.  calligraphy       /kəˈlɪɡrəfi/      n.    书法
7.  scared of                                  害怕；恐惧
14. give up                                    放弃
```

- Lines starting with a number + period are treated as word entries
- Entries under a `Proper Nouns / 专有名词` section are **excluded**
- The file may have header/metadata lines — these are automatically skipped

## Required Information (Ask the User)

Before running, you need:

1. **Input file path** — the source vocabulary `.txt` file
2. **N** — how many words to pick (e.g. 10, 20, 30, 40...)
3. **Output directory** — where to save the result

If the user does not specify N, **ask**: "How many words would you like? (e.g. 10, 20, 30, 40)"

Selection is always **random** (default behavior).

---

## Steps

1. **Ask for N** if not provided by user
2. **Run the script** using the terminal:

```bash
python3 .agent/skills/SchoolWork_WordTest_AnyNumber_Generator/scripts/pick_words.py \
  "<input_file>" \
  <N> \
  "<output_dir>"
```

3. **Confirm** the output file path to the user

That's it. The script handles everything else automatically.

---

## Output

A single `.txt` file saved to the specified output directory.

### Filename Format

```
{年级}_考单词_{单元}_{N}词_{YYYY.MM.DD}.txt
```

Examples:
```
8年级下_考单词_1单元_20词_2026.03.25.txt
8年级下_考单词_2单元_30词_2026.03.26.txt
7年级上_考单词_3单元_10词_2026.04.01.txt
```

- The grade and unit info are **inferred from the source filename** automatically
- The date is today's date (auto-generated)
- Multiple runs on the same day produce different random selections — each is saved with the same date but different content

### File Contents Format

```
8年级下 1单元 · 考单词（随机20词）
生成日期：2026.03.25
来源：初中8年级下_词汇表_Unit1_2026.03.25.txt

 1. *myself           /maɪˈself/        pron. 我自己
 2. *surprisingly     /səˈpraɪzɪŋli/    adv.  出人意料地；惊人地
 ...
20. *scared           /skeə(r)d/        adj.  害怕的；对……感到惊慌的
```

See `examples/8年级下_考单词_1单元_20词_2026.03.25.txt` for a full example.

---

## Example Usage

**User says:** "帮我从这个文件随机抽20个单词：初中8年级下_词汇表_Unit1_2026.03.25.txt，存到 8年级下_考单词 文件夹"

**Run:**
```bash
python3 .agent/skills/SchoolWork_WordTest_AnyNumber_Generator/scripts/pick_words.py \
  "/Users/zhaoqiang/.../8年级下_单词表/初中8年级下_词汇表_Unit1_2026.03.25.txt" \
  20 \
  "/Users/zhaoqiang/.../8年级下_考单词"
```

**Output:** `8年级下_考单词_1单元_20词_2026.03.25.txt`

---

## Script Location

```
.agent/skills/SchoolWork_WordTest_AnyNumber_Generator/
├── SKILL.md                   ← This file
├── scripts/
│   └── pick_words.py          ← THE script (always use this, never recreate)
└── examples/
    └── 8年级下_考单词_1单元_20词_2026.03.25.txt   ← Example output
```
