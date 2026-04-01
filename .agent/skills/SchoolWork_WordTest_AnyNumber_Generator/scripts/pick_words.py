#!/usr/bin/env python3
"""
SchoolWork_WordTest_AnyNumber_Generator — pick_words.py
========================================================
Randomly selects N words from a structured vocabulary TXT file and
writes a numbered, dated test-word list to the output directory.

Usage:
    python3 pick_words.py <input_file> <n> <output_dir>

Arguments:
    input_file  — Path to the source vocabulary .txt file
    n           — Number of words to pick (integer)
    output_dir  — Directory where the output file will be saved

Output filename format:
    {年级}_考单词_{单元}_{N}词_{YYYY.MM.DD}.txt
    e.g.  8年级下_考单词_1单元_20词_2026.03.25.txt

Exclusions (automatic):
    - The entire "Proper Nouns / 专有名词" section is skipped
    - Section headers like "Unit 1" are skipped
    - Any entry whose first word is a capitalised proper name
      (e.g. Luca, Bruno, Maya, India) is skipped
      → Rule: first token is ALL capitalised letters after stripping the
        number prefix, AND it has no phonetic /.../ or part-of-speech tag
"""

import random
import re
import sys
import os
from datetime import datetime


# Section headers that signal the start of a names-only block
PROPER_NOUN_MARKERS = [
    "Proper Nouns",
    "专有名词",
    "Proper Names",
    "固有名词",
]


def is_proper_name_entry(entry):
    """
    Return True if the entry looks like a standalone proper name.
    Detection rule: after removing the leading number, the first token
    starts with an uppercase letter AND the line has no phonetic /.../ 
    and no part-of-speech tag (n. v. adj. etc.).
    Examples that ARE skipped:  "1.  Luca   /ˈluːkə/  卢卡"  (has phonetic but is a name)
                                "2.  Bruno  /ˈbruːnəʊ/ 布鲁诺"
    We use a combined heuristic: first token is Title-case AND there is
    a Chinese-character translation but NO English part-of-speech abbreviation.
    """
    # Remove leading number
    body = re.sub(r'^\d+\.\s*', '', entry).strip()
    if not body:
        return False
    first_token = body.split()[0].rstrip('*')  # strip star prefix if present
    # Must start with uppercase
    if not first_token[0].isupper():
        return False
    # If it has a part-of-speech tag it is a common word (adj./n./v./adv./pron.)
    if re.search(r'\b(n\.|v\.|adj\.|adv\.|prep\.|conj\.|pron\.|interj\.|num\.)\b', entry):
        return False
    # If it has a Chinese translation but no POS → treat as proper name
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', entry))
    return has_chinese


def parse_entries(input_file):
    """
    Extract numbered word entries from the file.
    Automatically excludes:
      - Everything from a Proper Nouns section header onward
      - Individual entries that look like proper names (capitalised, no POS)
    """
    with open(input_file, encoding="utf-8") as f:
        lines = f.readlines()

    entries = []
    in_proper = False
    for line in lines:
        stripped = line.strip()
        # Stop at any proper-noun section header
        if any(marker in stripped for marker in PROPER_NOUN_MARKERS):
            in_proper = True
        if in_proper:
            continue
        # Must be a numbered entry
        if not (re.match(r'^\d+\.', stripped) and stripped):
            continue
        # Skip standalone proper names
        if is_proper_name_entry(stripped):
            continue
        entries.append(stripped)
    return entries


def infer_meta(basename):
    """Infer grade string and unit string from the source filename."""
    unit_match = re.search(r'[Uu]nit\s*(\d+)', basename)
    unit_str = f"{unit_match.group(1)}单元" if unit_match else "单元"

    grade_match = re.search(r'(\d+)年级([上下]?)', basename)
    grade_str = f"{grade_match.group(1)}年级{grade_match.group(2)}" if grade_match else "年级"

    return grade_str, unit_str


def reformat(idx, entry):
    cleaned = re.sub(r'^\d+\.\s*', '', entry)
    return f"{idx:2d}. {cleaned}"


def pick_words(input_file, n, output_dir):
    entries = parse_entries(input_file)
    total = len(entries)

    if n > total:
        print(f"⚠️  Requested {n} words but only {total} available. Using all {total}.")
        n = total

    selected = random.sample(entries, n)
    result_lines = [reformat(i + 1, e) for i, e in enumerate(selected)]

    basename = os.path.basename(input_file)
    grade_str, unit_str = infer_meta(basename)
    date_str = datetime.now().strftime("%Y.%m.%d")

    out_filename = f"{grade_str}_考单词_{unit_str}_{n}词_{date_str}.txt"
    out_path = os.path.join(output_dir, out_filename)

    header = (
        f"{grade_str} {unit_str} · 考单词（随机{n}词）\n"
        f"生成日期：{date_str}\n"
        f"来源：{basename}\n"
        f"\n"
    )
    content = header + "\n".join(result_lines) + "\n"

    os.makedirs(output_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Done! {n}/{total} words randomly selected.")
    print(f"📄 Output: {out_path}")
    print("\nSelected words:")
    for line in result_lines:
        print(line)

    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 pick_words.py <input_file> <n> <output_dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    n = int(sys.argv[2])
    output_dir = sys.argv[3]

    pick_words(input_file, n, output_dir)
