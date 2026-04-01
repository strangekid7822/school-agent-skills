---
name: SchoolWork_WordListExtractor
description: Extract vocabulary lists from textbook screenshots/images and convert them into structured text files with numbered entries, phonetics, translations, and related expressions.
---

# Word List Extractor (School Work)

This skill extracts vocabulary words from textbook screenshots/images and converts them into a well-structured, teacher-friendly text file format.

## When to Use

- When the user provides a screenshot or image of a vocabulary list (typically from a textbook)
- When the user wants to create study materials from textbook vocabulary pages
- When the user asks to "extract words" or "make a vocabulary file" from an image

## Input Requirements

1. **Image/Screenshot**: A vocabulary list image, typically from a textbook, containing:
   - English words with phonetic transcriptions
   - Part of speech indicators (n., v., adj., adv., etc.)
   - Chinese translations
   - Page numbers (optional)

## Output Format

Create a `.txt` file with the following structure:

### Header
```
Unit X Words and Expressions
```

### Word Entries - Regular Words
Each word should be formatted as:
```
[number]. [word] /[phonetic]/ [part of speech]. [Chinese translation]
```

Example:
```
1. fox /fɒks/ n. 狐狸
2. giraffe /dʒəˈrɑːf/ n. 长颈鹿
```

### Word Entries - Irregular Verbs (IMPORTANT!)
For irregular verbs, include the three principal forms **in the main entry line**:
```
[number]. [base form] - [past tense] - [past participle] /[phonetic]/ v. [Chinese translation]
```

Examples:
```
24. feed - fed - fed /fiːd/ v. 喂养; 饲养
25. leave - left - left /liːv/ v. 离开; 留下
36. hang - hung - hung /hæŋ/ v. 悬挂
39. become - became - become /bɪˈkʌm/ v. 变成; 成为
43. build - built - built /bɪld/ v. 创建; 建造
48. understand - understood - understood /ˌʌndəˈstænd/ v. 理解; 领会
```

**DO NOT** put verb tenses as separate sub-items like this:
```
❌ 24. feed /fiːd/ v. 喂养
      - (过去式) fed
```

### Related Expressions and Phrases

Add related expressions as sub-items with a `-` prefix and proper indentation:
```
6. care /keə(r)/ n. 照顾; 护理 v. 关心; 在乎
   - take care of = look after = care for 照顾; 照料
   - care about 关心; 在乎
```

### Enrichment Guidelines

#### 1. Prioritize Synonyms Over Specific Examples
Include words with similar meanings rather than specific usage examples:
```
✅ 5. arrive /əˈraɪv/ v. 到达
      - arrive at + 小地点 到达......
      - arrive in + 大地点 到达......
      - get to 到达
      - reach 到达

❌ 5. arrive /əˈraɪv/ v. 到达
      - arrive home 到家
      - arrive at school 到达学校
```

#### 2. Include Word Families (Same Pattern Words)
Group related words together:
```
16. everything /ˈevriθɪŋ/ pron. 每件事; 一切
    - anything /ˈænθɪŋ/ pron. 任何事物
    - nothing /ˈnʌθɪŋ/ pron. 没有事物
    - something /ˈsʌθɪŋ/ pron. 某事
```

#### 3. Include Parallel Structures
When a word is part of a pattern, include related patterns:
```
34. either /ˈaɪðə(r)/; /ˈiːðə(r)/ adv. 也 (用于否定词组后)
    - either ... or ... 要么......要么......
    - neither ... nor ... 既不......也不......
    - not only ... but also ... 不仅......而且......
```

#### 4. Include Related Words with Same Root
```
1. rule /ruːl/ n. 规则; 规章
   - follow the rules 遵守规则
   - break the rules 违反规则
   - ruler /ˈruːlə(r)/ n. 尺子;统治者
```

#### 5. Include Derivatives (Word Forms)
```
41. person /ˈpɜːsn/ n. 人
    - (pl.) people 或 persons
    - in person 亲自
    - personal /ˌpɜːsnəl/ adj. 个人的
```

### What to AVOID

#### 1. Do NOT Include Overly Basic Grammar Explanations
```
❌ - have to + 动词原形
❌ - don't have to 不必
❌ - has to (第三人称单数)
❌ - everything 作主语时，谓语动词用单数
❌ - 否定句中用 either，肯定句中用 too/also
```

#### 2. Use "do/not do" Format Instead of "动词原形"
```
✅ - had better + do 最好做某事
✅ - had better + not do 最好不做某事

❌ - had better + 动词原形 最好做某事
```

#### 3. Remove Redundant Similar Examples
Keep only the most essential phrase, avoid duplicates:
```
❌ - safety belt 安全带
    - seat belt 安全带
    
✅ - seat belt 安全带  (keep only one)
```

### Plural Forms

For irregular plurals, include them as sub-items:
```
4. wolf /wʊlf/ n. 狼
   - (pl.) wolves
```

### Proper Names Section

Separate proper names (人名) at the end:
```
Proper Names:
Mary /ˈmeəri/ 玛丽
Tony /ˈtəʊni/ 托尼
Anne /æn/ 安妮
Eric /ˈerɪk/ 埃里克
```

### Place Names Section

If there are place names, separate them at the end:
```
Place Names:
Antarctica /ænˈtɑːktɪkə/ 南极洲
Africa /ˈæfrɪkə/ 非洲
Thailand /ˈtaɪlænd/ 泰国
```

## File Naming Convention

Use this format:
```
[Grade]年级[Semester]_知识点_[Unit]单元_[Date].txt
```

Example: `7年级下_知识点_1单元_2026.01.10.txt`

## Processing Steps

1. **View the provided image** to identify all vocabulary words
2. **Group words by unit** as shown in the image
3. **Extract for each word**:
   - English word
   - Phonetic transcription (IPA format)
   - Part of speech (n., v., adj., adv., etc.)
   - Chinese translation(s)
   - For irregular verbs: include three principal forms in main line
4. **Add enrichment content**:
   - Synonyms and equivalent expressions
   - Word families (pronoun sets, parallel structures)
   - Related words with same root
   - Derivatives (noun/verb/adjective/adverb forms)
   - Essential phrases (not redundant examples)
5. **Separate proper names and place names** into dedicated sections
6. **Number entries sequentially** within each unit
7. **Save to the appropriate location** with proper filename

## Example Output

```
Unit 2 Words and Expressions

1. rule /ruːl/ n. 规则; 规章
   - follow the rules 遵守规则
   - break the rules 违反规则
   - ruler /ˈruːlə(r)/ n. 尺子;统治者
2. order /ˈɔːdə(r)/ n. 秩序; 命令 v. 点菜; 命令
   - in order 按顺序; 井然有序
   - in order to 为了
   - keep order 维持秩序
3. follow /ˈfɒləʊ/ v. 遵循; 跟随
   - follow sb. 跟随某人
   - follow one's advice 听从某人的建议
4. late /leɪt/ adj. 迟的; 晚的
   - be late for 迟到
5. arrive /əˈraɪv/ v. 到达
   - arrive at + 小地点 到达......
   - arrive in + 大地点 到达......
   - get to 到达
   - reach 到达
...
24. feed - fed - fed /fiːd/ v. 喂养; 饲养
    - feed sb./sth. 喂......
    - feed on 以......为食
25. leave - left - left /liːv/ v. 离开; 留下
    - leave for 动身去......
    - leave sb. alone 让某人独处
...

Proper Names:
Mary /ˈmeəri/ 玛丽
Tony /ˈtəʊni/ 托尼
```

## Tips

- Always verify phonetic transcriptions for accuracy
- Ensure Chinese translations match the textbook context
- Prioritize synonyms and related words over specific usage examples
- Include word families and parallel structures
- Keep entries concise - no redundant similar examples
- Use "do/not do" format instead of "动词原形"
- Put irregular verb tenses in the main entry line, not as sub-items

## Continuous Improvement

> [!IMPORTANT]
> **After using this skill**, if you identify any improvements that could make it better (e.g., new formatting patterns, additional content types, better organization, edge cases not covered), **always ask the user** whether they would like to update this skill file.
>
> Examples of potential improvements:
> - New vocabulary patterns discovered (e.g., phrasal verbs, idioms)
> - Better formatting for specific content types
> - Additional sections needed (e.g., example sentences, usage notes)
> - Refined file naming conventions
> - New grammar note patterns
>
> **How to ask**: "I noticed [specific improvement]. Would you like me to update the SchoolWork_WordListExtractor skill to include this?"
