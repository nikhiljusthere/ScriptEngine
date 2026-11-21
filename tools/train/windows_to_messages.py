"""Convert simple window JSONL to messages-format for verify_row_wiki.py."""
import json, sys
from pathlib import Path

def convert(infile, outfile):
    with open(infile) as fin, open(outfile, "w") as fout:
        for line in fin:
            d = json.loads(line.strip())
            passage = d.get("passage", "")
            page = d.get("page", "")
            section = d.get("section", "")
            
            # Match the format that verify_row_wiki.py expects:
            # messages[1]["content"] should be "Series: jjk\nPage: ...\nSection: ...\n\nPassage:\n..."
            # The verifier extracts passage via: .split("Passage:\n", 1)[1]
            msg1_content = f"Series: jjk\nPage: {page}\nSection: {section}\n\nPassage:\n{passage}"
            
            out = {"id": d["id"], "page": page, "section": section}
            out["messages"] = [
                {"role": "system", "content": ""},
                {"role": "user", "content": msg1_content},
                {"role": "assistant", "content": ""}
            ]
            fout.write(json.dumps(out, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <input_windows.jsonl> <output_messages.jsonl>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
    print(f"Converted {sys.argv[1]} -> {sys.argv[2]}")
