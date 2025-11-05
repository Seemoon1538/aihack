# src/ai/local_llm.py — v16.0
from transformers import pipeline
import re
import logging

logging.getLogger("transformers").setLevel(logging.ERROR)

try:
    generator = pipeline("text-generation", model="gpt2", max_length=100, truncation=True)
except:
    generator = None

def generate_payload(prompt: str) -> str:
    if not generator:
        return None
    try:
        result = generator(prompt, max_new_tokens=50, num_return_sequences=1)
        return result[0]["generated_text"].split("\n")[0].strip()
    except:
        return None

def extract_tokens(text: str):
    from .token_patterns import TOKENS
    found = []
    for typ, data in TOKENS.items():
        if "regex" in data:
            matches = re.findall(data["regex"], text)
            found.extend([(typ, m) for m in matches])
    return found