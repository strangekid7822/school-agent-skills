---
name: SchoolWork_GaokaoPaperToTxt
description: Extract Gaokao English paper content from screenshots and format it into a structured text document. Supports 单项选择, 语法填空, 完形填空, 阅读理解 (A/B/C/D), 七选五, and 任务型阅读.
---

# Gaokao Paper to Text

This skill extracts English exam content from screenshots and converts it into a clean, standardized text format. The user will specify which section type is being processed.

---

## Inline Formatting in 原文

When text in the **原文 (passage)** section is visually formatted in the screenshot, mark it inline using these symbols:

- **Underlined** → `__word or phrase__` (double underscore on each side)
- **Bold** → `**word or phrase**`

Rules:
- Apply in **all sections** — 原文, 习题, 选项, 答案解析, and any other section.
- Wrap the exact span that is formatted, including any punctuation that is part of the formatting.
- If a word is both bold and underlined, apply both: `**__word__**`.
- Do not add markers for italics or other formatting not listed above.

Example:
```
His live shows showed __enthusiastic__ people in China.
Scientists are still trying to determine how **harmful** microplastics are.
```

---

## Two Global Rules (Read First)

### Rule 1 — 答案解析 is conditional
**Do NOT generate 答案解析 unless the user explicitly requests it** (e.g., "with answers", "include explanations", "加答案解析"). If not requested, omit the entire 答案解析 section and its header from the output.

### Rule 2 — 重点词汇 is always filled in by the model
For every section type, the model must select ~20 essential Gaokao vocabulary items from the passage and questions and fill them in using this format:

```
word/phrase - part of speech. Chinese definition
```

Examples:
```
pollution - n. 污染
rely on - 依赖于，依靠
potential - adj. 潜在的；n. 潜力
settle - v. （使）沉降；（常用义）定居，解决
```

Rules for selection:
- Pick single words AND collocations/phrases (e.g., `lead to`, `focus on`)
- Prioritize high-frequency Gaokao vocabulary
- Note 熟词生义 (familiar words with less common meanings in context) where relevant
- Never leave this section empty
- Keep Chinese definitions and explanations as concise as possible — one short phrase is enough

---

## Section Types & Extraction Rules

### 单项选择 (Single-Answer Multiple Choice)

**Extract:**
1. All questions with their options, preserving the original numbering and the `(   )` answer bracket at the start of each item.
2. Options may be 3 or 4 per question — reproduce exactly what appears in the screenshot.
3. **Answers and explanations are always model-generated** (no answer key exists in the screenshots — this overrides Rule 1). Determine the correct answer and write a concise Chinese explanation that also addresses key wrong options.
4. Vocabulary: fill in ~10–15 essential grammar structures, collocations, and content words drawn from the questions. Include the Chinese definition for every item, using the same `word/phrase - part of speech. Chinese definition` format as other section types.
5. Difficult sentence translation: pick one representative sentence from the questions for translation practice.

**Title format:** `[paper origin]_单项选择`
The paper origin comes from the user's instruction or the screenshot context (e.g., `2021中考模拟题库_英语试卷1_单项选择`).

**Answer format for 答案解析:**

```
N.X 考查[语法点] 【解析】...（briefly address key wrong options）...故选X。
```

Use these 语法点 labels (choose the most accurate one per question):
- 考查冠词用法
- 考查非谓语动词
- 考查固定搭配
- 考查形容词最高级
- 考查make复合宾语结构
- 考查不定代词
- 考查定语从句主谓一致
- 考查感叹句结构
- 考查宾语从句的语序与时态
- 考查[其他语法点] — use a clear Chinese label if none of the above fit

**Output template:**
```text
单项选择_[paper origin]
========================================

【单项选择·习题】

(   )1. [question stem]
        A. [option]    B. [option]    C. [option]

(   )2. [question stem]
        A. [option]    B. [option]    C. [option]    D. [option]

...

【单项选择·答案解析】

1.B 考查冠词用法 【解析】...故选B。

2.A 考查非谓语动词 【解析】...故选A。

...

【单项选择·重点词汇】

word1 - part of speech. Chinese definition
phrase1 - Chinese definition
grammar pattern - explanation of use

...

【单项选择·难句翻译】

[English sentence from one of the questions]
[Chinese translation]

========================================
```

---

### 语法填空 (Grammar Fill-in-the-Blank)

**Extract:**
1. The reading passage. Reformat any numbered blanks to `___[number]___` format (e.g., `56` or `56 _________` → `___56___`).
2. Answers and explanations for each blank — **only if the user requests 答案解析** (see Rule 1).
3. Difficult sentence translation (长难句): if present in the screenshots, extract ONLY the English sentence and its Chinese translation. If absent, omit the section entirely — do not invent one.
4. Vocabulary: fill in ~20 essential Gaokao words/phrases (see Rule 2).

**Output template:**
```text
[Title]
========================================

【语法填空·习题】

[Passage with ___N___ blanks]

【语法填空·答案解析】         ← omit entirely if not requested

[Numbered answers and explanations]

【语法填空·重点词汇】

word1 - part of speech. definition
word2 - part of speech. definition
...

【语法填空·难句翻译】

[English sentence]
[Chinese translation]

========================================
```

---

### 完形填空 (Cloze Test)

**Extract:**
1. The passage with blanks formatted as `___N___`.
2. All options for each blank (A/B/C/D), preserving original numbering.
3. Answers and explanations — **only if the user requests 答案解析** (see Rule 1).
4. Difficult sentence translation: same rule — extract only if present, otherwise omit.
5. Vocabulary: fill in ~20 essential Gaokao words/phrases (see Rule 2).

**Output template:**
```text
[Title]
========================================

【完形填空·习题】

[Passage with ___N___ blanks]

【完形填空·选项】

41. A. [option]    B. [option]    C. [option]    D. [option]
42. ...

【完形填空·答案解析】         ← omit entirely if not requested

[Numbered answers and explanations]

【完形填空·重点词汇】

word1 - part of speech. definition
word2 - part of speech. definition
...

【完形填空·难句翻译】

[English sentence]
[Chinese translation]

========================================
```

---

### 阅读理解 A / B / C / D (Reading Comprehension)

**Extract:**
1. The full reading passage.
2. All multiple-choice questions with their four options (A / B / C / D), keeping original question numbers.
3. Answers and explanations — **only if the user requests 答案解析** (see Rule 1). When generating, follow the answer format below precisely.
4. Difficult sentence translation: same rule as 语法填空 — extract only if present, otherwise omit.
5. Vocabulary: fill in ~20 essential Gaokao words/phrases (see Rule 2).

The section label (A, B, C, or D) comes from the user's instruction or the screenshot context.

**Answer format for 答案解析 (when requested):**

Use these 题型 labels:
- 写作手法题 — questions about how the author writes/presents
- 细节理解题 — factual detail questions
- 推理判断题 — inference/reasoning questions

For **推理判断题**, include a 【定位句】block:
```
N.X 推理判断题 【定位句】[exact English sentence from text]（第X段第Y句）
译文 [Chinese translation of the 定位句]
【解析】...故选X。
```

For **写作手法题** and **细节理解题**:
```
N.X 写作手法题 【解析】...故选X。
N.X 细节理解题 【解析】...故选X。
```

**Output template:**
```text
[Title]
========================================

【阅读理解X·原文】

[Full passage]

【阅读理解X·习题】

21. [Question text]
A. [option]   B. [option]   C. [option]   D. [option]

22. ...

【阅读理解X·答案解析】         ← omit entirely if not requested

21.C 写作手法题 【解析】...故选C。

22.A 细节理解题 【解析】...故选A。

23.B 推理判断题 【定位句】[English sentence]（第X段第Y句）
译文 [Chinese translation]
【解析】...故选B。

【阅读理解X·重点词汇】

word1 - part of speech. definition
word2 - part of speech. definition
...

【阅读理解X·难句翻译】

[English sentence]
[Chinese translation]

========================================
```
*(Replace `X` with A, B, C, or D as appropriate.)*

---

### 七选五 (7-Choose-5)

**Extract:**
1. The passage with blanks, formatted as `___[number]___`.
2. All seven option sentences (A–G), each on its own line.
3. Answers and explanations — **only if the user requests 答案解析** (see Rule 1).
4. Difficult sentence translation: same rule — extract only if present, otherwise omit.
5. Vocabulary: fill in ~20 essential Gaokao words/phrases (see Rule 2).

**Output template:**
```text
[Title]
========================================

【七选五·原文】

[Passage with ___N___ blanks]

【七选五·选项】

A. [sentence]
B. [sentence]
C. [sentence]
D. [sentence]
E. [sentence]
F. [sentence]
G. [sentence]

【七选五·答案解析】         ← omit entirely if not requested

36.X 考查上下文逻辑关系 【解析】...

【七选五·重点词汇】

word1 - part of speech. definition
word2 - part of speech. definition
...

【七选五·难句翻译】

[English sentence]
[Chinese translation]

========================================
```

---

### 任务型阅读 (Task-based Reading)

**Extract:**
1. The full reading passage.
2. The task prompt and its structure exactly as shown (table, outline, bullet list, etc.).
3. Answers — **only if the user requests 答案解析** (see Rule 1).
4. Difficult sentence translation: same rule — extract only if present, otherwise omit.
5. Vocabulary: fill in ~20 essential Gaokao words/phrases (see Rule 2).

**Output template:**
```text
[Title]
========================================

【任务型阅读·原文】

[Full passage]

【任务型阅读·任务】

[Task prompt and structure — table, outline, etc. — reproduced in plain text]

【任务型阅读·答案解析】         ← omit entirely if not requested

[Numbered answers and explanations]

【任务型阅读·重点词汇】

word1 - part of speech. definition
word2 - part of speech. definition
...

【任务型阅读·难句翻译】

[English sentence]
[Chinese translation]

========================================
```

---

## General Rules (All Types)

- Output everything inside a **plain text code block**.
- **Title format:** The first line must be `[PaperOrigin]_[SectionType]` (e.g., `2021中考模拟题库_英语试卷1_单项选择`, `2023高考真题_全国卷I_阅读理解D`). The paper origin comes from the user's instruction or the screenshot context.
- Preserve original question/blank numbering from the screenshots.
- Never invent answers, sentences, or vocabulary — extract only what is visible.
- **答案解析 explanations:** Address key wrong options briefly — do not make each explanation overly long.
- **重点词汇 format:** Every item must include its Chinese definition, using `word/phrase - part of speech. Chinese definition` (see 阅读理解 example). Mix single words and collocations/grammar patterns as appropriate.
- If a section has no content (e.g., no difficult sentence), omit that section entirely rather than leaving a blank header.
- **Output file:** Unless the user specifies a path, save the result as a `.txt` file in `/Users/zhaoqiang/Library/CloudStorage/OneDrive-Personal/School/教学部门/08_初高中资料/11_SkillWorkSpace`. When done, reply with only a markdown link to the file — no other commentary.
- **Be concise:** Do not explain your work, summarize steps, or add any text beyond the file link when finished.

## Examples

- **单项选择 example:** `examples/example_output_danxiangxuanze.txt`
- **语法填空 example:** `examples/example_output_yufatiankong.txt`
- **完形填空 example:** `examples/example_output_wanxingtiankong.txt`
- **七选五 example:** `examples/example_output_qixuanwu.txt`
- **阅读理解 example:** `examples/example_output_yuedulijie.txt`
