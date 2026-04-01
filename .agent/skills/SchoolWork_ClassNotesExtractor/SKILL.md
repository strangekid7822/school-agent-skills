---
name: SchoolWork_ClassNotesExtractor
description: Extract useful vocabulary words and phrases from raw class notes .txt files. Filters out question answers and grammar exercise fillers, and outputs a clean, structured vocabulary reference file.
---

# Class Notes Extractor (School Work)

This skill reads raw class notes `.txt` files (typically transcribed during English lessons) and extracts all genuinely useful vocabulary words and phrases into a clean, structured reference file.

## When to Use

- When the user provides a raw class notes `.txt` file from an English lesson
- When the user says "extract words/phrases from my notes" or "make a vocab list from class notes"
- When the note file contains a mix of vocabulary entries and question answers that need to be separated

## Input Requirements

A `.txt` file containing class notes in a numbered format, e.g.:

```
1. off
   let off steam    发泄
2. being criticized
   by + 动作发出者        被动语态：be done
   constantly              adv. 一直
3. concern          v. 担心
   concerning       prep. 有关
```

- Items are numbered (1., 2., 3., etc.)
- The **word/phrase directly after the number** is typically a fill-in-the-blank **answer to a question** — skip it
- Sub-items (indented lines below each number) are vocabulary words, phrases, and grammar notes

## What to Include vs. Exclude

### ✅ INCLUDE
- Vocabulary words with part of speech and Chinese translation
- Useful phrases (phrasal verbs, set expressions, collocations)
- Word families grouped under the same root (e.g., survive / survivor / survival)
- Grammar-adjacent phrases that function as vocabulary (e.g., `attach importance to`, `take sth. into account`)

### ❌ EXCLUDE
- The single word or phrase appearing immediately after a question number — these are **fill-in-the-blank answers** (e.g., `off`, `being criticized`, `taken`, `is being exhibited`)
- Pure grammar rule explanations without vocabulary value (e.g., `by + 动作发出者`, `am/is/are being done`)
- Overly basic words students already know
- Duplicate entries

## Output Format

Create a `.txt` file with the following structure:

### Header
```
[Grade] 课堂笔记提炼
日期：YYYY.MM.DD
来源：[source filename]
========================================
```

### Section 1 — Phrases (短语)
```
【短语 Phrases】
phrase_here            Chinese meaning
phrase_here            Chinese meaning
```

- Align Chinese meanings in a column using tabs/spaces for readability
- Include phrasal verbs, prepositional phrases, idiomatic expressions, collocations

### Section 2 — Vocabulary (单词)
```
【单词 Vocabulary】
word        pos.    Chinese meaning
word        pos.    Chinese meaning
```

- Include part of speech: `n.`, `v.`, `adj.`, `adv.`, `prep.`, etc.
- Align columns consistently
- List word families together (e.g., `survive`, `survivor`, `survival` in sequence)
- If a word has multiple parts of speech, use `n./v.` format

## File Naming Convention

```
[Grade]_课堂笔记提炼_[YYYY.MM.DD].txt
```

Example: `高一下_课堂笔记提炼_2026.02.26.txt`

## Output Location

Save to the appropriate class notes directory:
- 高一: `10_Classes Notes/2026_高一/`
- 高二: `10_Classes Notes/2026_高二/`
- 高三: `10_Classes Notes/2026_高三/`

(Or wherever the user specifies.)

## Processing Steps

1. **Read the source `.txt` file** in full
2. **Identify question answers**: The word/phrase on the same line as the question number (e.g., `1. off`, `9. taken`) — **skip these**
3. **Collect sub-items**: All indented lines under each number are candidates
4. **Filter sub-items**:
   - Keep: vocabulary words with POS + Chinese, useful phrases with Chinese meaning
   - Skip: pure grammar meta-notes (e.g., `by + 动作发出者`, `be done`, `am/is/are being done`)
5. **Categorize**:
   - Multi-word expressions/phrases → **短语 Phrases** section
   - Single words → **单词 Vocabulary** section
6. **Group word families** together in the Vocabulary section (e.g., `survive` / `survivor` / `survival`)
7. **Format and align** columns for readability
8. **Write the output file** with the correct filename to the correct directory

## Example Output

```
高一下 课堂笔记提炼
日期：2026.02.26
来源：2026_Week 09_高一_2026.02.26.txt
========================================

【短语 Phrases】
let off steam              发泄
in/with relief             松了一口气
so far                     迄今为止
attach importance to...    重视...
take sth. into account     把...考虑在内
at present                 此刻；现在
look down upon             藐视；瞧不起
get rid of                 摆脱
put up with sb.            忍受某人
give birth to...           生下...
in the hope of             希望...

========================================

【单词 Vocabulary】
constantly          adv.    一直
concern             v.      担心
concerning          prep.   有关
concerned           adj.    担心的
generation          n.      一代人
tough               adj.    艰难的
bare                adj.    光着的
barely              adv.    几乎不；仅仅
exhibit             v.      展览
extraordinary       adj.    不凡的
impress             v.      给...留下印象
impression          n.      印象
colleague           n.      同事
extend              v.      延长；扩大
extensive           adj.    广泛的
specialize          v.      从事专门研究
lively              adj.    充满活力的；热闹的
reflect             v.      反射；反映
master              n./v.   大师；掌握
mastery             n.      掌握；精湛技艺
repeatedly          adv.    反复地
survive             v.      生存；幸存
survivor            n.      幸存者
survival            n.      幸存
heartbroken         adj.    心碎的
pray                v.      祈祷
prayer              n.      祈祷
adopt               v.      领养
biological          adj.    生物学的
unite               v.      使联合
reunite             v.      使重聚
faith               n.      信仰
separate            v.      使...分开
desperate           adj.    绝望的
```

## Real Examples

See the `examples/` folder for a complete real-world pair:

| File | Description |
|---|---|
| `examples/example_input_高一_2026.02.26.txt` | Raw class notes source file (numbered fill-in-the-blank format) |
| `examples/example_output_高一下_课堂笔记提炼_2026.02.26.txt` | Clean extracted vocabulary output |

These examples are taken directly from a real 高一 English class session on 2026.02.26 and show both the filtering of question answers and the final two-section output format.

## Tips

- Question numbers in source files are **not always sequential** (e.g., jumps from 10 to 36) — process all entries regardless of number gaps
- Some source notes mix grammar exercise numbers with vocabulary — always use the "is this immediately after a number?" test to detect answers
- Word families (e.g., survive/survivor/survival, pray/prayer) should be listed consecutively
- Preserve Chinese translations exactly as written in the notes

## Continuous Improvement

> [!IMPORTANT]
> **After using this skill**, if you identify any improvements (e.g., new note formats, better filtering rules, additional output sections), **always ask the user** whether they would like to update this skill file.
>
> Examples of potential improvements:
> - New source file formats encountered
> - Better rules for distinguishing answers from vocabulary
> - Additional output sections (e.g., grammar patterns worth keeping)
> - Refined file naming conventions
>
> **How to ask**: "I noticed [specific improvement]. Would you like me to update the SchoolWork_ClassNotesExtractor skill to include this?"
