"""
Step 4: Query decomposition for multi-hop questions + Qwen generation
This handles complex questions that require multiple retrieval passes.
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# import retriever from step 3
from python.step3_retrieval import HybridRetriever

# ── Config ────────────────────────────────────────────────────────────────────
QWEN_MODEL_PATH  = "Qwen/Qwen2.5-7B-Instruct"   # or your local path
MAX_NEW_TOKENS   = 1024
CONTEXT_LIMIT    = 6000    # chars of retrieved context to pass to Qwen


# ─────────────────────────────────────────────────────────────────────────────
# 4A. Load Qwen on GPU
# ─────────────────────────────────────────────────────────────────────────────

class QwenModel:
    _model     = None
    _tokenizer = None

    @classmethod
    def load(cls):
        if cls._model is None:
            print(f"Loading {QWEN_MODEL_PATH}...")
            cls._tokenizer = AutoTokenizer.from_pretrained(QWEN_MODEL_PATH)
            cls._model = AutoModelForCausalLM.from_pretrained(
                QWEN_MODEL_PATH,
                torch_dtype=torch.bfloat16,
                device_map="cuda",
            )
            cls._model.eval()
            print("Qwen loaded.")
        return cls._model, cls._tokenizer

    @classmethod
    def generate(cls, prompt: str, max_new_tokens: int = MAX_NEW_TOKENS) -> str:
        model, tokenizer = cls.load()
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(text, return_tensors="pt").to("cuda")

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,          # greedy — more deterministic/accurate
                temperature=1.0,
                pad_token_id=tokenizer.eos_token_id
            )

        # decode only new tokens
        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


# ─────────────────────────────────────────────────────────────────────────────
# 4B. Query classifier — is this a simple or multi-hop question?
# ─────────────────────────────────────────────────────────────────────────────

MULTIHOP_SIGNALS = [
    "which characters",
    "who else",
    "what other",
    "compare",
    "all techniques",
    "everyone who",
    "list all",
    "relationship between",
    "how are .* related",
    "what happened .* after",
    "why did .* lead to",
]


def is_multihop(query: str) -> bool:
    query_lower = query.lower()
    for signal in MULTIHOP_SIGNALS:
        if re.search(signal, query_lower):
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# 4C. Query decomposer — breaks complex query into sub-questions
# ─────────────────────────────────────────────────────────────────────────────

DECOMPOSE_PROMPT = """You are a query decomposition assistant for a Jujutsu Kaisen wiki.

Break the following complex question into 2-4 simpler sub-questions that can each be answered independently. Each sub-question should target a specific fact or entity.

Output ONLY a JSON list of strings. No explanation.

Question: {query}

Output format: ["sub-question 1", "sub-question 2", ...]"""


def decompose_query(query: str) -> List[str]:
    """Use Qwen to decompose a complex query into simpler sub-questions."""
    prompt = DECOMPOSE_PROMPT.format(query=query)
    response = QwenModel.generate(prompt, max_new_tokens=256)

    # parse JSON from response
    try:
        # find JSON array in response
        match = re.search(r'\[.*?\]', response, re.DOTALL)
        if match:
            sub_questions = json.loads(match.group())
            # validate
            if isinstance(sub_questions, list) and all(isinstance(q, str) for q in sub_questions):
                return sub_questions[:4]  # max 4 sub-questions
    except (json.JSONDecodeError, AttributeError):
        pass

    # fallback — return original query
    return [query]


# ─────────────────────────────────────────────────────────────────────────────
# 4D. Build context string from retrieved chunks + graph
# ─────────────────────────────────────────────────────────────────────────────

def build_context(
    chunks: List[Dict],
    graph_relations: List[Dict],
    char_limit: int = CONTEXT_LIMIT
) -> str:
    """
    Build a clean context string for Qwen.
    Includes retrieved chunks and relevant graph relationships.
    """
    parts = []

    # graph relations first (very compact, high information density)
    if graph_relations:
        parts.append("=== Known Relationships ===")
        seen_relations = set()
        for rel in graph_relations[:20]:  # cap to avoid bloat
            line = f"- {rel['source']} → {rel['relation']} → {rel['related']}"
            if line not in seen_relations:
                parts.append(line)
                seen_relations.add(line)
        parts.append("")

    # retrieved chunks
    parts.append("=== Retrieved Passages ===")
    total_chars = sum(len(p) for p in parts)

    for i, chunk in enumerate(chunks):
        doc   = chunk["payload"]["doc_title"]
        sec   = chunk["payload"]["section"]
        text  = chunk["text"]
        entry = f"[{i+1}] Source: {doc} / {sec}\n{text}"

        if total_chars + len(entry) > char_limit:
            break

        parts.append(entry)
        parts.append("")
        total_chars += len(entry)

    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# 4E. Answer generation prompts
# ─────────────────────────────────────────────────────────────────────────────

ANSWER_PROMPT = """You are an expert on the Jujutsu Kaisen manga/anime series.

Answer the question using ONLY the information provided in the context below. If the context does not contain enough information to answer confidently, say so clearly.

Be specific, accurate, and cite which source passage your answer comes from (e.g. "According to [1]...").

Context:
{context}

Question: {question}

Answer:"""


MERGE_PROMPT = """You are an expert on the Jujutsu Kaisen series.

The following are answers to sub-questions that together answer the main question. Synthesize them into a single, coherent, accurate answer. Do not add information not present in the sub-answers.

Main Question: {main_question}

Sub-answers:
{sub_answers}

Final Answer:"""


# ─────────────────────────────────────────────────────────────────────────────
# 4F. Main QA pipeline
# ─────────────────────────────────────────────────────────────────────────────

class RAGPipeline:
    def __init__(self):
        self.retriever = HybridRetriever()

    def answer_simple(self, query: str) -> Dict:
        """Single-pass retrieval + generation."""
        chunks, graph_relations = self.retriever.retrieve(query)
        context = build_context(chunks, graph_relations)

        prompt = ANSWER_PROMPT.format(context=context, question=query)
        answer = QwenModel.generate(prompt)

        return {
            "query":    query,
            "answer":   answer,
            "sources":  [
                {
                    "doc":     c["payload"]["doc_title"],
                    "section": c["payload"]["section"],
                    "score":   c.get("rerank_score", 0),
                    "text":    c["text"][:200]
                }
                for c in chunks
            ],
            "graph_relations": graph_relations
        }

    def answer_multihop(self, query: str) -> Dict:
        """Decompose → retrieve per sub-question → merge answers."""
        # decompose
        sub_questions = decompose_query(query)
        print(f"  Decomposed into {len(sub_questions)} sub-questions:")
        for sq in sub_questions:
            print(f"    - {sq}")

        # answer each sub-question independently
        sub_answers = []
        all_sources = []

        for sq in sub_questions:
            chunks, graph_relations = self.retriever.retrieve(sq)
            context = build_context(chunks, graph_relations)
            prompt  = ANSWER_PROMPT.format(context=context, question=sq)
            answer  = QwenModel.generate(prompt, max_new_tokens=512)

            sub_answers.append(f"Q: {sq}\nA: {answer}")
            all_sources.extend(chunks)

        # merge sub-answers into final answer
        merge_prompt = MERGE_PROMPT.format(
            main_question=query,
            sub_answers="\n\n".join(sub_answers)
        )
        final_answer = QwenModel.generate(merge_prompt, max_new_tokens=MAX_NEW_TOKENS)

        # deduplicate sources
        seen_ids = set()
        unique_sources = []
        for c in all_sources:
            if c["chunk_id"] not in seen_ids:
                unique_sources.append(c)
                seen_ids.add(c["chunk_id"])

        return {
            "query":         query,
            "answer":        final_answer,
            "sub_questions": sub_questions,
            "sub_answers":   sub_answers,
            "sources": [
                {
                    "doc":     c["payload"]["doc_title"],
                    "section": c["payload"]["section"],
                    "score":   c.get("rerank_score", 0),
                    "text":    c["text"][:200]
                }
                for c in unique_sources[:FINAL_TOP_K]
            ]
        }

    def ask(self, query: str) -> Dict:
        """
        Main entry point.
        Automatically routes to simple or multi-hop pipeline.
        """
        print(f"\nQuery: {query}")

        if is_multihop(query):
            print("  → Multi-hop pipeline")
            return self.answer_multihop(query)
        else:
            print("  → Simple pipeline")
            return self.answer_simple(query)


# ─────────────────────────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pipeline = RAGPipeline()

    # simple question
    result = pipeline.ask("What is Evening Moon Sword Drawing?")
    print("\nAnswer:", result["answer"])
    print("\nSources:")
    for s in result["sources"]:
        print(f"  - {s['doc']} / {s['section']} (score: {s['score']:.3f})")

    print("\n" + "="*60)

    # multi-hop question
    result = pipeline.ask(
        "Which characters used barrier techniques during the Shibuya Incident Arc?"
    )
    print("\nAnswer:", result["answer"])
    if "sub_questions" in result:
        print("\nSub-questions used:")
        for sq in result["sub_questions"]:
            print(f"  - {sq}")
