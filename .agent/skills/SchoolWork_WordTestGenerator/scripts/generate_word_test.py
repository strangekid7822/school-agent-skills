import os
import re
import sys
import random
import datetime
import shutil
import argparse

def parse_line(line):
    # Regex for: "1. word /phonetic/ n. meaning"
    # Matches: number, word, spacing, phonetic (optional), rest
    # Note: Phonetic might be missing or different format.
    # We want to extract:
    # - Word token (for Answer key clean version)
    # - Full English part (including phonetic for display if needed? 
    #   Wait, Answer key needs "EN_WORD" with NO phonetics. 
    #   Test key needs "EN_WORD" empty.
    #   The input file has "word /phonetic/ n. meaning".
    #   We need to split Chinese and English.
    
    # Simple split by first occurrence of Chinese character?
    # Or split by parts of speech?
    
    # Strategy:
    # 1. Remove leading number "1. "
    # 2. Split into potential English and Chinese parts.
    #    Usually Chinese starts after the phonetic and part of speech.
    #    "rule /ruːl/ n. 规则; 规章"
    #    English part: "rule /ruːl/ n." ?? No.
    #    The template requires: 
    #    Test: #, ZH, (Empty En)
    #    Answer: #, ZH, EN
    
    # Let's look at the "English Column Rules" in SKILL.md:
    # - Write ONLY the English word or phrase.
    # - REMOVE all phonetics.
    # - "hallway /'hɔ:lwei/" -> "hallway"
    
    # So we need to distinct:
    # 1. Chinese Meaning containing pos: "n. 规则; 规章"
    # 2. English word: "rule"
    
    # Regex approach:
    # ^\d+\.\s+ (?P<en_raw>.*?) \s+ (?P<rest>([a-z]+\.\s+)?[\u4e00-\u9fa5].*|([a-z]+\.\s+).*)$ ??
    # It's tricky because POS (n., v.) is usually the separator.
    
    # Let's try to capture the English word at the start.
    # It usually ends before a slash /.../ or before a POS.
    pass

def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

def parse_file(filepath):
    words = []
    current_lines = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == "Proper Names:":
            break
            
        # Check if line starts with number
        match = re.match(r'^(\d+)\.\s+(.*)', line)
        if match:
            # Parse previous word if any (not needed as we treat line by line? 
            # Wait, what about sub-points "- related phrase"?
            # The Example Input shows sub-points.
            # The Output Format (Table Rows) implies we just list the main words?
            # Or do we include phrases?
            # SKILL.md says: 
            # "Group words into pairs... Row Format... #L ZH EN..."
            # It DOES NOT explicitly say to include the phrases.
            # The format seems to be for the numbered items.
            # However, usually dictations include phrases if they are numbered?
            # The input file has "1. rule... - follow...".
            # Usually strict word dictation uses the main words. 
            # Let's stick to the numbered items for now unless instructed otherwise.
            # "extract vocabulary words... Number... English word... Chinese meaning... Skip Proper Names"
            # It doesn't mention the bullet points. I will include ONLY numbered items.
            
            num = match.group(1)
            content = match.group(2)
            
            # Content: "rule /ruːl/ n. 规则; 规章"
            # We need to split into English Word (cleaned) and Chinese (including POS)
            
            # Heuristic: split by first Chinese char?
            # Or find the first POS marker (n. v. adj. adv. prep. conj. pron.)?
            # Or assume phonetic is in /.../?
            
            # Step 1: separate EN and CN part.
            # Find index of first Chinese char.
            first_cn_idx = -1
            for i, char in enumerate(content):
                if '\u4e00' <= char <= '\u9fa5':
                    first_cn_idx = i
                    break
            
            if first_cn_idx != -1:
                # But notice "n. " precedes Chinese.
                # scan backwards from Chinese to find the start of the meaning (POS).
                # content[:first_cn_idx] is roughly "rule /ruːl/ n. "
                # We want "n. 规则..." as Chinese column (usually).
                # Actually, looking at template: col-zh "中文".
                # Usually we put POS + Chinese in Chinese col.
                
                # Refined split:
                # Look for common POS patterns: " n.", " v.", " adj.", " adv.", " prep.", " conj."
                # Be careful.
                
                # Let's try to isolate the English Word for the Answer Key first.
                # Remove /.../ or [...] phonetics.
                
                en_part_raw = content[:first_cn_idx].strip() # "rule /ruːl/ n."
                cn_part = content[first_cn_idx:] # "规则; 规章"
                
                # Check for POS at end of en_part_raw
                # Common POS list
                pos_list = ['n.', 'v.', 'adj.', 'adv.', 'prep.', 'conj.', 'pron.', 'num.', 'art.', 'int.', 'pl.']
                found_pos = ""
                for pos in pos_list:
                    if en_part_raw.endswith(pos):
                        found_pos = pos
                        en_part_raw = en_part_raw[:-len(pos)].strip()
                        break
                
                # Re-assemble Chinese part with POS
                if found_pos:
                    cn_display = f"{found_pos} {cn_part}"
                else:
                    cn_display = cn_part
                    
                # Clean English part: remove phonetics /.../
                en_clean = re.sub(r'\/.*\/', '', en_part_raw)
                en_clean = re.sub(r'\[.*\]', '', en_clean)
                en_clean = en_clean.strip()
                
                words.append({
                    'num': num,
                    'en_clean': en_clean,
                    'zh_display': cn_display,
                    'raw': line
                })
            else:
                # No Chinese found? Maybe all English or Just english + pos?
                # Just take it as is.
                words.append({
                    'num': num,
                    'en_clean': content,
                    'zh_display': '',
                    'raw': line
                })

    return words

def generate_rows(words, mode='test'):
    # mode: 'test' (empty English), 'answer' (filled English)
    rows = []
    
    # Pair words: 0&1, 2&3...
    # If odd, last one is alone.
    
    total = len(words)
    i = 0
    while i < total:
        w1 = words[i]
        w2 = words[i+1] if i+1 < total else None
        
        # Format: 
        # <tr><td>#L</td><td>ZH</td><td>EN</td><td class="spacer"></td><td>#R</td><td>ZH</td><td>EN</td></tr>
        
        # Left
        l_num = w1['num']
        l_zh = w1['zh_display']
        l_en = w1['en_clean'] if mode == 'answer' else ''
        
        # Right
        if w2:
            r_num = w2['num']
            r_zh = w2['zh_display']
            r_en = w2['en_clean'] if mode == 'answer' else ''
        else:
            r_num = ''
            r_zh = ''
            r_en = ''
            
        row = f"""<tr>
    <td class="col-num">{l_num}</td>
    <td class="col-zh">{l_zh}</td>
    <td class="col-en">{l_en}</td>
    <td class="col-spacer"></td>
    <td class="col-num">{r_num}</td>
    <td class="col-zh">{r_zh}</td>
    <td class="col-en">{r_en}</td>
</tr>"""
        rows.append(row)
        i += 2
        
    return "\n".join(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help="Path to input .txt file")
    parser.add_argument('--order', choices=['original', 'random'], default='original', help="Order of words")
    args = parser.parse_args()
    
    input_path = os.path.abspath(args.input_file)
    input_dir = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    
    # Parse filename for info
    # Example: 7年级下_知识点_2单元_2026.01.16.txt
    # We generally want to extract "7年级下" and "2单元"
    # Fallback to defaults if regex fails
    
    grade = ""
    unit = ""
    
    # Try to find grade "X年级X"
    m_grade = re.search(r'(\d+年级[上下]?)', filename)
    if m_grade:
        grade = m_grade.group(1)
        
    # Try to find unit "X单元"
    m_unit = re.search(r'(\d+单元)', filename)
    if m_unit:
        unit = m_unit.group(1)
        
    subtitle = f"{grade} · {unit}" if grade and unit else filename
    
    # Parse words
    words = parse_file(input_path)
    
    if args.order == 'random':
        random.shuffle(words)
        # Update numbers? No, usually keep original numbers to track? 
        # Or re-number 1..N?
        # Dictation usually implies re-numbering 1..N for the test paper layout.
        # Let's re-number them for the output table so they look sequential.
        for idx, w in enumerate(words):
            w['num'] = str(idx + 1)
            
    total_words = len(words)
    
    # Date for filename
    today_str = datetime.datetime.now().strftime("%Y.%m.%d")
    
    # Read Template
    # Assuming script is in .agent/skills/.../scripts/, template is in ../resources/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Adjust if we are running this from somewhere else? 
    # __file__ should give us the location.
    # Resources is sibling to scripts
    skill_dir = os.path.dirname(script_dir)
    template_path = os.path.join(skill_dir, 'resources', 'template.html')
    
    if not os.path.exists(template_path):
        print(f"Error: Template not found at {template_path}")
        sys.exit(1)
        
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
        
    # Check for Logo
    logo_src = os.path.join(skill_dir, 'resources', 'teacher_logo.jpg')
    logo_dest = os.path.join(input_dir, 'teacher_logo.jpg')
    if os.path.exists(logo_src):
        if not os.path.exists(logo_dest):
            shutil.copy2(logo_src, logo_dest)
            print("Copied teacher_logo.jpg to output directory.")
    else:
        print("Warning: teacher_logo.jpg not found in resources.")

    # Generate Test HTML
    order_str = "乱序" if args.order == 'random' else "正序"
    lines_test = generate_rows(words, mode='test')
    
    html_test = template_content.replace('{{TITLE}}', '单词默写测验')
    html_test = html_test.replace('{{SUBTITLE}}', subtitle)
    html_test = html_test.replace('{{TOTAL}}', str(total_words))
    html_test = html_test.replace('{{TABLE_ROWS}}', lines_test)
    
    out_name_test = f"{grade}_{unit}_单词默写_{order_str}_{today_str}.html"
    # Cleanup filename (remove emptyParts if regex failed)
    out_name_test = out_name_test.replace('__', '_').strip('_')
    out_path_test = os.path.join(input_dir, out_name_test)
    
    with open(out_path_test, 'w', encoding='utf-8') as f:
        f.write(html_test)
    print(f"Generated Test HTML: {out_path_test}")
    
    # Generate Answer HTML
    lines_ans = generate_rows(words, mode='answer')
    
    html_ans = template_content.replace('{{TITLE}}', '单词默写测验 (答案)')
    html_ans = html_ans.replace('{{SUBTITLE}}', subtitle)
    html_ans = html_ans.replace('{{TOTAL}}', str(total_words))
    html_ans = html_ans.replace('{{TABLE_ROWS}}', lines_ans)
    
    out_name_ans = f"{grade}_{unit}_单词默写_{order_str}_{today_str}_答案.html"
    out_name_ans = out_name_ans.replace('__', '_').strip('_')
    out_path_ans = os.path.join(input_dir, out_name_ans)
    
    with open(out_path_ans, 'w', encoding='utf-8') as f:
        f.write(html_ans)
    print(f"Generated Answer HTML: {out_path_ans}")

if __name__ == "__main__":
    main()
