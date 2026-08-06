"""Tokenize a small sample with annotations to inspect tokenizer behavior.

Phase 1: works only with tiktoken (cl100k_base / o200k_base) — the most
commonly compared baseline. Other tokenizers will report 'install required'.
"""

from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Tokenize a sample text and annotate.")
    parser.add_argument("text", help="Text to tokenize (or '-' for stdin)")
    parser.add_argument(
        "--tokenizer", default="cl100k_base", choices=["cl100k_base", "o200k_base"], help="tiktoken encoding name"
    )
    parser.add_argument("--show-tokens", action="store_true", help="Show token strings (not just IDs)")
    args = parser.parse_args()

    try:
        import tiktoken
    except ImportError:
        print(
            json.dumps(
                {
                    "error": "tiktoken not installed",
                    "install": "pip install tiktoken",
                    "note": "Phase 1 only supports tiktoken for sample segmentation.",
                },
                indent=2,
            )
        )
        return 2

    text = sys.stdin.read() if args.text == "-" else args.text
    enc = tiktoken.get_encoding(args.tokenizer)
    ids = enc.encode(text)
    n_words = len(text.split())
    n_tokens = len(ids)
    fertility = n_tokens / n_words if n_words > 0 else float("inf")

    out = {
        "text_preview": text[:200] + ("…" if len(text) > 200 else ""),
        "tokenizer": args.tokenizer,
        "n_words": n_words,
        "n_tokens": n_tokens,
        "fertility": round(fertility, 3),
        "byte_fallback_tokens": sum(1 for t in [enc.decode([i]) for i in ids] if any(c == "�" for c in t)),
    }
    if args.show_tokens:
        out["tokens"] = [enc.decode([i]) for i in ids]
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
