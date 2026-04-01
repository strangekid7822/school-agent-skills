---
name: SchoolWork_PDFVocabExtractor
description: Convert PDF vocabulary pages to PNG images and extract vocabulary into structured JSON files with false meanings for quiz apps.
---

# PDF Vocabulary Extractor

Extract vocabulary from PDF textbook pages and generate JSON files for quiz applications.

## When to Use

- User provides a PDF file containing vocabulary pages (e.g., textbook word lists)
- User wants to create quiz data from vocabulary pages
- User asks to "extract vocabulary" or "make vocabulary JSON" from a PDF

## Workflow

### Step 1: PDF to PNG Conversion

Convert PDF pages to PNG images using `pdftoppm`:

```bash
# Create output directory
mkdir -p .agent/workspace/pdf_extractor/output

# Convert PDF to PNG (200 DPI for good readability)
pdftoppm -png -r 200 "INPUT_PDF_PATH" ".agent/workspace/pdf_extractor/output/page"
```

### Step 2: View and Extract with AI Vision

Use `view_file` on each PNG to read the vocabulary content. The AI model's vision capability extracts text directly—no OCR library needed.

### Step 3: Confirm Textbook (MANDATORY)

> [!CAUTION]
> **STOP! You MUST get user confirmation before proceeding.**
> Do NOT generate any JSON until the user confirms the textbook name from the list below.

Ask the user: "Which textbook is this vocabulary from?"

**Valid options (choose one):**
| Code | Textbook |
|------|----------|
| 1 | 人教版_2011版_7年级上 |
| 2 | 人教版_2011版_7年级下 |
| 3 | 人教版_2011版_8年级上 |
| 4 | 人教版_2011版_8年级下 |
| 5 | 人教版_2011版_9年级 |
| 6 | 人教版_2022版_7年级上 |
| 7 | 人教版_2022版_7年级下 |
| 8 | 人教版_2022版_8年级上 |
| 9 | 人教版_2022版_8年级下 |

**Wait for user response before continuing.**

After user confirms the textbook, generate JSON with this exact structure:

```json
{
  "textbooks": [
    {
      "source_file": "人教版_2022版_7年级上",
      "vocabulary": [
        {
          "unit": "Unit 1",
          "word": "start",
          "phonetic": "/stɑːt/",
          "part_of_speech": "v.",
          "meaning": "开始；着手",
          "false_meanings": ["结束；完成", "休息；暂停"]
        },
        {
          "unit": "Unit 1",
          "word": "goose",
          "phonetic": "/ɡuːs/",
          "part_of_speech": "n.",
          "meaning": "鹅",
          "false_meanings": ["猫", "狗"]
        },
        {
          "unit": "Unit 1",
          "word": "make friends",
          "phonetic": "",
          "part_of_speech": "v.",
          "meaning": "交朋友",
          "false_meanings": ["做作业", "吃早餐"],
          "is_phrase": true
        },
        {
          "unit": "Unit 1",
          "word": "New York",
          "phonetic": "/nuː jɔːk/",
          "part_of_speech": "n.",
          "meaning": "纽约",
          "false_meanings": ["伦敦", "巴黎"],
          "is_phrase": true,
          "is_proper_noun": true
        }
      ]
    }
  ]
}
```

## Critical Structure Rules

1. **Root must be `textbooks` array** — not a flat object
2. **Each textbook has `source_file`** — the textbook name
3. **`unit` goes inside each vocabulary entry** — not at root level

## Field Requirements

**Root level:**
| Field | Required | Description |
|-------|----------|-------------|
| `textbooks` | ✅ | Array of textbook objects |

**Each textbook:**
| Field | Required | Description |
|-------|----------|-------------|
| `source_file` | ✅ | Textbook name (confirm with user, e.g., "人教版七年级上册") |
| `vocabulary` | ✅ | Array of word entries |

**Each vocabulary entry:**
| Field | Required | Description |
|-------|----------|-------------|
| `unit` | ✅ | Unit/chapter name exactly as shown |
| `word` | ✅ | English word or phrase |
| `phonetic` | ✅ | IPA pronunciation from source |
| `part_of_speech` | ✅ | e.g., "n.", "v.", "adj.", "adv." |
| `meaning` | ✅ | Correct Chinese meaning |
| `false_meanings` | ✅ | Array of exactly **2** wrong Chinese meanings |
| `is_phrase` | ❌ | Optional. Set `true` only for multi-word phrases |
| `is_proper_noun` | ❌ | Optional. Set `true` for person names, place names, or organization names |

## Generating False Meanings

Create **2** clearly distinct wrong Chinese translations. The quiz is for kids, so options must be easy to distinguish.

### Rules

1. **Match structure**: If correct meaning has `；` (e.g., "开始；着手"), false meanings must also have `；` (e.g., "结束；完成"). If single meaning, false meanings stay single too.
2. **Same part of speech**: If word is a noun, false meanings should also be nouns
3. **Different category**: Options should be clearly different concepts
4. **NOT too similar**: Avoid near-synonyms or words that could confuse students
5. **No duplicates**: Both must be different from each other and from correct meaning

### Good Examples ✅

```json
// Multi-meaning word: "start" (开始；着手) - false meanings also have ；
"meaning": "开始；着手",
"false_meanings": ["结束；完成", "休息；暂停"]

// Single-meaning word: "goose" (鹅) - false meanings stay single
"meaning": "鹅",
"false_meanings": ["猫", "狗"]

// "bottle" (瓶子) - different objects, clearly distinct
"meaning": "瓶子",
"false_meanings": ["书包", "铅笔"]
```

### Bad Examples ❌

```json
// STRUCTURE MISMATCH - real has ；but false doesn't!
"meaning": "开始；着手",
"false_meanings": ["结束", "休息"]  // ❌ Missing ；

// TOO SIMILAR - confusing for kids!
"false_meanings": ["杯子", "盒子"]  // both containers
"false_meanings": ["走", "跳"]  // both movement verbs
```

## Directory Structure

```
.agent/workspace/pdf_extractor/
├── input/          # Place PDF files here
├── output/         # Generated PNG files
└── json/           # Generated JSON output files
```

## Skill Resources

```
.agent/skills/SchoolWork_PDFVocabExtractor/
├── SKILL.md                      # This file
├── scripts/
│   └── convert_pdf.sh            # Reusable PDF→PNG conversion script
└── examples/
    └── sample_output.json        # Reference JSON output format
```

### Using the Script

```bash
# From workspace root
.agent/skills/SchoolWork_PDFVocabExtractor/scripts/convert_pdf.sh "input.pdf" "output_dir" 200
```

## File Naming

Output JSON: `{grade}_{textbook}_{unit}.json`

Examples:
- `7年级上_Starter_Unit_1.json`
- `7年级上_Unit_1.json`
- `7年级上_Unit_2.json`

## Processing Steps

1. **Locate PDF** in `.agent/workspace/pdf_extractor/input/`
2. **Convert to PNG** using pdftoppm command
3. **View each PNG** with view_file tool
4. **Extract vocabulary** entries (word, phonetic, part of speech, meaning, unit)
5. **Generate false_meanings** for each word (2 plausible wrong answers, matching structure)
6. **Mark phrases** with `is_phrase: true` for multi-word entries
7. **Save JSON** to `.agent/workspace/pdf_extractor/json/`

## Notes

- Words < 3 letters will be auto-filtered by the quiz app
- Only add `is_phrase: true` for phrases; omit field for single words
- Preserve exact phonetic transcriptions from source
- Keep unit names exactly as shown in the textbook
