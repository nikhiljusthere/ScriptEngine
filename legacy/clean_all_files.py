import os
import re
from pathlib import Path

def clean_text(content):
    """Clean and format text content"""
    
    # Remove citation brackets like [1], [2], etc. (including those with spaces)
    content = re.sub(r'\[\s*\d+\s*\]', '', content)
    
    # Remove citation brackets with words/letters like [?] etc
    content = re.sub(r'\[\s*[a-zA-Z?]+\s*\]', '', content)
    
    # Fix multiple spaces
    content = re.sub(r'  +', ' ', content)
    
    # Fix multiple spaces around punctuation
    content = re.sub(r'\s+([.,;:!?])', r'\1', content)
    
    # Remove excessive line breaks (more than 2 consecutive)
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Fix spacing after periods at start of lines
    content = re.sub(r'\n\s+', '\n', content)
    
    # Fix line breaks that should be spaces (text flowing between lines)
    # Join lines that don't end with punctuation
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        line = line.rstrip()
        if line and i < len(lines) - 1 and not any(line.endswith(p) for p in ['.', ':', '?', '!', '-', '–', '—']):
            # Check if next line starts with a capital letter (likely new sentence/section)
            next_line = lines[i+1].lstrip() if i+1 < len(lines) else ''
            if next_line and next_line[0].isupper() and len(fixed_lines) > 0:
                # This might be a section header, keep as is
                fixed_lines.append(line)
            elif next_line and next_line[0].islower():
                # Continuation of paragraph
                line = line + ' '
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix inconsistent spacing around colons
    content = re.sub(r'\s*:\s*', ': ', content)
    
    # Remove trailing whitespace from lines
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)
    
    # Remove empty lines at the beginning and end
    content = content.strip()
    
    # Remove consecutive empty lines (keep max 1)
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Fix common capitalization inconsistencies
    replacements = {
        'jujutsu high': 'Jujutsu High',
        'jujutsu': 'Jujutsu',
        'cursed energy': 'Cursed Energy',
        'cursed spirit': 'Cursed Spirit',
        'cursed technique': 'Cursed Technique',
        'cursed object': 'Cursed Object',
        'domain expansion': 'Domain Expansion',
        'domain barrier': 'Domain Barrier',
        'innate domain': 'Innate Domain',
        'simple domain': 'Simple Domain',
        'shikigami': 'Shikigami',
        'binding vow': 'Binding Vow',
        'cursed energy': 'Cursed Energy',
        'tokyo jujutsu high': 'Tokyo Jujutsu High',
        'kyoto jujutsu high': 'Kyoto Jujutsu High',
    }
    
    for old, new in replacements.items():
        # Only replace at word boundaries to avoid changing mid-word
        pattern = r'\b' + re.escape(old) + r'\b'
        content = re.sub(pattern, new, content, flags=re.IGNORECASE)
    
    # Remove duplicate consecutive section headers
    content = re.sub(r'^(\d+\s+[A-Za-z\s]+)\n\1$', r'\1', content, flags=re.MULTILINE)
    
    return content


def clean_all_files(directory):
    """Clean all text files in directory"""
    path = Path(directory)
    
    if not path.exists():
        print(f"Directory not found: {directory}")
        return
    
    txt_files = list(path.glob('*.txt'))
    print(f"Found {len(txt_files)} text files to clean")
    
    cleaned_count = 0
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            cleaned_content = clean_text(content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            cleaned_count += 1
            print(f"✓ Cleaned: {file_path.name}")
        
        except Exception as e:
            print(f"✗ Error cleaning {file_path.name}: {e}")
    
    print(f"\nCompleted! Cleaned {cleaned_count}/{len(txt_files)} files")


if __name__ == "__main__":
    directory = r"E:\VS CODE\Midnight Render\Softwares\RAG\data\jjk\clean"
    clean_all_files(directory)
