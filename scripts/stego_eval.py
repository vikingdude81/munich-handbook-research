#!/usr/bin/env python3
"""
stego_eval.py — Steganography Research Evaluation

Tests whether a frontier LLM can break Porta's cipher systems from De Occultis
Literarum Notis (1592) WITHOUT being given the key.

This is a real eval for historical knowledge depth + cryptanalysis capability.
Each cipher type is tested at three difficulty levels:
  - easy:   short common-word message, obvious statistical signature
  - medium: mixed message, some noise
  - hard:   long message, multiple words, maximum ambiguity

Cipher systems tested:
  1. Myth Tokens     (Apollo=A, Scorpius=S ...)  — cultural knowledge required
  2. Zodiac Numeric  (A=♈1, B=♉1 ...)           — pattern recognition
  3. Null/Acrostic   (first letter of each word) — NLP + contextual reading
  4. Saturn/Reversed (A↔Z, B↔Y ...)             — frequency analysis
  5. Caesar variants (Jupiter+4, Mars+5, Sun+6)  — classical cryptanalysis
  6. Pigpen/Symbol   (conceptual test)           — symbol system knowledge

Usage:
    python scripts/stego_eval.py                    # run all evals
    python scripts/stego_eval.py --cipher myth      # run one cipher type
    python scripts/stego_eval.py --difficulty easy  # one difficulty level
    python scripts/stego_eval.py --dry-run          # show what would be sent, no API calls
    python scripts/stego_eval.py --out logs/stego_eval_results.json

Model: nvidia/nemotron-3-nano-omni via LM Studio at http://192.168.50.150:1234
"""

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path

from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
LM_STUDIO_URL = "http://192.168.50.150:1234/v1"
MODEL = "nvidia/nemotron-3-nano-omni"
DEFAULT_OUT = Path("logs/stego_eval_results.json")

# ── Cipher implementations (matching porta_cipher_wheel.html) ─────────────────

ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

MYTH_TOKENS = {
    "A": "Apollo", "B": "Brutus", "C": "Cicero", "D": "Diana",
    "E": "Endymion", "F": "Fortuna", "G": "Gorgo", "H": "Hermes",
    "I": "Iris", "J": "Jove", "K": "Kronos", "L": "Luna",
    "M": "Mars", "N": "Nemesis", "O": "Osiris", "P": "Proteus",
    "Q": "Quirinus", "R": "Raphael", "S": "Scorpius", "T": "Tammuz",
    "U": "Uranus", "V": "Venus", "W": "Wisdom", "X": "Xerxes",
    "Y": "Yule", "Z": "Zazel",
}

ZODIAC = [
    ("Aries", "♈"), ("Taurus", "♉"), ("Gemini", "♊"), ("Cancer", "♋"),
    ("Leo", "♌"), ("Virgo", "♍"), ("Libra", "♎"), ("Scorpio", "♏"),
    ("Sagittarius", "♐"), ("Capricorn", "♑"), ("Aquarius", "♒"), ("Pisces", "♓"),
]

FILLERS = {
    "A": ["All", "And", "After", "Among", "Above"],
    "B": ["By", "But", "Before", "Below", "Beyond"],
    "C": ["Can", "Come", "Called", "Certain", "Carried"],
    "D": ["Do", "Day", "Dark", "Deep", "Divine"],
    "E": ["Each", "Even", "Ever", "Eternal", "Enter"],
    "F": ["For", "From", "Find", "Far", "First"],
    "G": ["God", "Given", "Great", "Guard", "Gate"],
    "H": ["He", "Has", "His", "Holy", "High"],
    "I": ["In", "Is", "Into", "Inner", "Indeed"],
    "J": ["Just", "Join", "Journey", "Jupiter", "Judge"],
    "K": ["Keep", "Known", "King", "Knowledge", "Key"],
    "L": ["Let", "Like", "Light", "Lord", "Luna"],
    "M": ["My", "More", "Most", "Moon", "Mark"],
    "N": ["Not", "Now", "Near", "Night", "Name"],
    "O": ["Of", "On", "One", "Only", "Open"],
    "P": ["Put", "Per", "Path", "Power", "Planet"],
    "Q": ["Quite", "Queen", "Quick", "Quiet", "Quintus"],
    "R": ["Read", "Right", "Ring", "Revealed", "Remain"],
    "S": ["So", "Said", "Sign", "Sun", "Saturn"],
    "T": ["The", "That", "This", "Through", "True"],
    "U": ["Upon", "Under", "Until", "Up", "Unseen"],
    "V": ["Very", "Via", "Voice", "Virtue", "Veiled"],
    "W": ["With", "When", "While", "Word", "Without"],
    "X": ["Xerxes", "XI", "XII", "X-rays", "Xanthe"],
    "Y": ["Yet", "You", "Your", "Yonder", "Years"],
    "Z": ["Zazel", "Zeal", "Zone", "Zenith", "Zero"],
}


def encode_myth(text: str) -> str:
    return " · ".join(MYTH_TOKENS.get(c, c) for c in text.upper() if c.isalpha())


def encode_zodiac(text: str) -> str:
    tokens = []
    for c in text.upper():
        if not c.isalpha():
            continue
        idx = ALPHABET.index(c)
        sign_name, sign_sym = ZODIAC[idx % 12]
        pos = idx // 12 + 1
        tokens.append(f"{sign_name}{pos}")
    return " ".join(tokens)


def encode_null(text: str, seed: int = 0) -> str:
    words = []
    for i, c in enumerate(text.upper()):
        if not c.isalpha():
            continue
        opts = FILLERS.get(c, [c])
        words.append(opts[(seed + i) % len(opts)])
    return " ".join(words)


def encode_reversed(text: str) -> str:
    return "".join(ALPHABET[25 - ALPHABET.index(c)] if c.isalpha() else c
                   for c in text.upper())


def encode_caesar(text: str, shift: int) -> str:
    return "".join(
        ALPHABET[(ALPHABET.index(c) + shift) % 26] if c.isalpha() else c
        for c in text.upper()
    )


# ── Test message bank ─────────────────────────────────────────────────────────

TEST_MESSAGES = {
    "easy": [
        "HELP",
        "MARS",
        "FLEE",
    ],
    "medium": [
        "MEET AT DAWN",
        "SEND THE KEY",
        "BELLA FORTISSIME",
    ],
    "hard": [
        "THE MESSENGER ARRIVES BEFORE MIDNIGHT",
        "SATURN GOVERNS THE BINDING OF SECRETS",
        "ALL KNOWLEDGE IS HIDDEN FROM THE UNINITIATED",
    ],
}

# ── Prompt templates ──────────────────────────────────────────────────────────

PROMPTS = {
    "myth_tokens": {
        "system": (
            "You are a Renaissance scholar and cryptanalyst specializing in 16th-century "
            "Italian natural magic and cryptography. You have deep knowledge of "
            "Giambattista della Porta's works."
        ),
        "user_template": (
            "The following text was found in a 16th-century manuscript alongside "
            "a list of planetary correspondences. It may be a cipher message. "
            "Analyze it and attempt to decode it. Explain your reasoning step by step.\n\n"
            "Text: {ciphertext}\n\n"
            "What is the hidden message, if any? What cipher system is being used?"
        ),
        "hint_template": (
            "This text uses a substitution system described in De Occultis Literarum Notis "
            "by Giambattista della Porta (1592). Each mythological name represents a letter. "
            "Try to decode: {ciphertext}"
        ),
    },
    "zodiac_numeric": {
        "system": (
            "You are a cryptanalyst and historian of Renaissance occult sciences. "
            "You are familiar with planetary hour systems, zodiacal correspondences, "
            "and early modern cipher techniques."
        ),
        "user_template": (
            "Analyze this sequence of zodiac signs and numbers found in a 16th-century "
            "manuscript. It may encode a hidden message using a cipher where each sign "
            "and number represents a letter of the alphabet. Attempt to decode it.\n\n"
            "Sequence: {ciphertext}\n\n"
            "What pattern do you see? Can you decode the message?"
        ),
        "hint_template": (
            "The twelve zodiac signs are numbered 1 and 2 (and sometimes 3), "
            "corresponding to letters in alphabetical order. Aries1=A, Taurus1=B... "
            "Aries2=M, Taurus2=N... Decode: {ciphertext}"
        ),
    },
    "null_acrostic": {
        "system": (
            "You are a cryptanalyst specializing in steganography — the art of hiding "
            "messages within innocent-looking text. You are familiar with acrostic "
            "ciphers used in Renaissance correspondence."
        ),
        "user_template": (
            "The following phrase was found in a 16th-century letter. It may contain "
            "a hidden message. Look carefully at the structure of the words.\n\n"
            "Text: {ciphertext}\n\n"
            "Is there a hidden message here? How was it concealed?"
        ),
        "hint_template": (
            "This uses a null cipher — the message is concealed in the first letter "
            "of each word. Extract the first letter of every word to find the message: "
            "{ciphertext}"
        ),
    },
    "saturn_reversed": {
        "system": (
            "You are an expert cryptanalyst. Analyze cipher texts and identify "
            "the encoding method and original plaintext."
        ),
        "user_template": (
            "Decode this cipher text. It was produced using a simple classical "
            "substitution method. Use frequency analysis or pattern recognition "
            "to identify the system and recover the original message.\n\n"
            "Cipher: {ciphertext}\n\n"
            "What is the plaintext? What cipher system was used?"
        ),
        "hint_template": (
            "This uses a reversed alphabet cipher (A=Z, B=Y, C=X...) — "
            "the method della Porta calls 'retrogando ordine'. Decode: {ciphertext}"
        ),
    },
    "caesar_jupiter": {
        "system": (
            "You are an expert cryptanalyst. Use frequency analysis and pattern "
            "recognition to decode classical cipher texts."
        ),
        "user_template": (
            "Decode this cipher text using frequency analysis or brute force. "
            "It is a classical substitution cipher.\n\n"
            "Cipher: {ciphertext}\n\n"
            "Identify the shift value and recover the plaintext."
        ),
        "hint_template": (
            "This is a Caesar cipher. The shift value corresponds to Jupiter's "
            "number (4). Each letter is shifted forward by 4 positions. Decode: {ciphertext}"
        ),
    },
}

# ── Eval runner ───────────────────────────────────────────────────────────────

CIPHER_ENCODERS = {
    "myth_tokens":     lambda msg: encode_myth(msg),
    "zodiac_numeric":  lambda msg: encode_zodiac(msg),
    "null_acrostic":   lambda msg: encode_null(msg),
    "saturn_reversed": lambda msg: encode_reversed(msg),
    "caesar_jupiter":  lambda msg: encode_caesar(msg, 4),
}


def score_response(response: str, plaintext: str) -> dict:
    """Score the model's response against the known plaintext."""
    resp_upper = response.upper()
    plain_upper = plaintext.upper()
    plain_words = [w for w in plain_upper.split() if w.isalpha()]

    # Exact match
    if plain_upper in resp_upper:
        return {"score": "exact", "matched_words": len(plain_words), "total_words": len(plain_words)}

    # Word-level match
    matched = [w for w in plain_words if w in resp_upper]
    ratio = len(matched) / len(plain_words) if plain_words else 0

    if ratio >= 0.8:
        return {"score": "strong", "matched_words": len(matched), "total_words": len(plain_words)}
    elif ratio >= 0.5:
        return {"score": "partial", "matched_words": len(matched), "total_words": len(plain_words)}
    elif ratio >= 0.2:
        return {"score": "weak", "matched_words": len(matched), "total_words": len(plain_words)}
    else:
        return {"score": "fail", "matched_words": len(matched), "total_words": len(plain_words)}


def run_eval(client: OpenAI, cipher_name: str, plaintext: str,
             difficulty: str, with_hint: bool = False, dry_run: bool = False) -> dict:
    """Run a single eval: encode the message, ask the LLM to decode it."""
    encoder = CIPHER_ENCODERS[cipher_name]
    ciphertext = encoder(plaintext)
    prompt_cfg = PROMPTS[cipher_name]

    if with_hint:
        user_msg = prompt_cfg["hint_template"].format(ciphertext=ciphertext)
    else:
        user_msg = prompt_cfg["user_template"].format(ciphertext=ciphertext)

    result = {
        "cipher": cipher_name,
        "difficulty": difficulty,
        "plaintext": plaintext,
        "ciphertext": ciphertext,
        "with_hint": with_hint,
        "timestamp": datetime.now().isoformat(),
    }

    if dry_run:
        result["dry_run"] = True
        result["would_send"] = {
            "system": prompt_cfg["system"],
            "user": user_msg,
        }
        print(f"\n[DRY RUN] {cipher_name} / {difficulty} / hint={with_hint}")
        print(f"  Plaintext:  {plaintext}")
        print(f"  Ciphertext: {ciphertext[:80]}{'...' if len(ciphertext) > 80 else ''}")
        return result

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": prompt_cfg["system"]},
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": "Analysis:\n\n"},
            ],
            max_tokens=1024,
            temperature=0.2,
        )
        # Extract content (handles reasoning model output)
        content = resp.choices[0].message.content or ""
        if not content and hasattr(resp.choices[0].message, "reasoning_content"):
            content = resp.choices[0].message.reasoning_content or ""

        scoring = score_response(content, plaintext)
        result["response"] = content
        result["score"] = scoring["score"]
        result["matched_words"] = scoring["matched_words"]
        result["total_words"] = scoring["total_words"]

        marker = {"exact": "EXACT", "strong": "STRONG", "partial": "PARTIAL",
                  "weak": "WEAK", "fail": "FAIL"}.get(scoring["score"], "?")
        print(f"  [{marker}] {cipher_name} / {difficulty} / hint={with_hint} | {plaintext!r}")
        if scoring["score"] in ("partial", "weak", "fail"):
            # Print first 200 chars of response for quick review
            print(f"           Response: {content[:200].strip()!r}")

    except Exception as e:
        result["error"] = str(e)
        result["score"] = "error"
        print(f"  [ERROR] {cipher_name} / {difficulty}: {e}")

    return result


# ── Summary report ────────────────────────────────────────────────────────────

def print_summary(results: list[dict]):
    """Print a summary table of eval results."""
    print("\n" + "=" * 72)
    print("STEGANOGRAPHY EVAL SUMMARY")
    print("=" * 72)

    ciphers = list(CIPHER_ENCODERS.keys())
    difficulties = ["easy", "medium", "hard"]
    score_vals = {"exact": 3, "strong": 2, "partial": 1, "weak": 0.5, "fail": 0, "error": 0}

    for cipher in ciphers:
        cipher_results = [r for r in results if r["cipher"] == cipher and not r.get("dry_run")]
        if not cipher_results:
            continue
        print(f"\n{cipher.upper().replace('_', ' ')}")
        for diff in difficulties:
            dr = [r for r in cipher_results if r["difficulty"] == diff]
            for r in dr:
                hint_tag = " [hint]" if r.get("with_hint") else ""
                score = r.get("score", "?")
                matched = r.get("matched_words", 0)
                total = r.get("total_words", 1)
                print(f"  {diff:8} {hint_tag or '       '} -> {score:8} "
                      f"({matched}/{total} words)  plaintext={r['plaintext']!r}")

    # Aggregate stats
    scored = [r for r in results if r.get("score") and r.get("score") != "error" and not r.get("dry_run")]
    if scored:
        avg = sum(score_vals.get(r["score"], 0) for r in scored) / (3 * len(scored))
        print(f"\nOverall score: {avg:.1%} of maximum")

        # Best and worst
        by_score = sorted(scored, key=lambda r: score_vals.get(r["score"], 0), reverse=True)
        print(f"Best:  {by_score[0]['cipher']} / {by_score[0]['difficulty']} -> {by_score[0]['score']}")
        print(f"Worst: {by_score[-1]['cipher']} / {by_score[-1]['difficulty']} -> {by_score[-1]['score']}")

    print("=" * 72)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Stego eval: can the LLM break Porta's ciphers?")
    parser.add_argument("--cipher", choices=list(CIPHER_ENCODERS.keys()) + ["all"],
                        default="all", help="Which cipher to test")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard", "all"],
                        default="all", help="Difficulty level")
    parser.add_argument("--with-hint", action="store_true",
                        help="Also run each eval with a hint (tells model which system)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be sent without making API calls")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="Output JSON file for results")
    args = parser.parse_args()

    # Select ciphers and difficulties
    ciphers = list(CIPHER_ENCODERS.keys()) if args.cipher == "all" else [args.cipher]
    diffs = ["easy", "medium", "hard"] if args.difficulty == "all" else [args.difficulty]

    client = None if args.dry_run else OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")

    results = []
    total = len(ciphers) * len(diffs) * len(TEST_MESSAGES["easy"]) * (2 if args.with_hint else 1)
    print(f"Running {total} eval cases across {len(ciphers)} cipher(s), {len(diffs)} difficulty level(s)")
    print(f"Model: {MODEL} @ {LM_STUDIO_URL}\n")

    for cipher in ciphers:
        print(f"\n--- {cipher.upper().replace('_', ' ')} ---")
        for diff in diffs:
            messages = TEST_MESSAGES[diff]
            for msg in messages:
                # Without hint
                r = run_eval(client, cipher, msg, diff, with_hint=False, dry_run=args.dry_run)
                results.append(r)
                if not args.dry_run:
                    time.sleep(0.5)  # avoid overwhelming LM Studio

                # With hint (optional)
                if args.with_hint:
                    r2 = run_eval(client, cipher, msg, diff, with_hint=True, dry_run=args.dry_run)
                    results.append(r2)
                    if not args.dry_run:
                        time.sleep(0.5)

    print_summary(results)

    # Save results
    if not args.dry_run:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        existing = []
        if args.out.exists():
            try:
                existing = json.loads(args.out.read_text())
            except Exception:
                pass
        args.out.write_text(json.dumps(existing + results, indent=2))
        print(f"\nResults saved to {args.out}")
    else:
        print("\n[Dry run complete — no API calls made, no results saved]")


if __name__ == "__main__":
    main()
