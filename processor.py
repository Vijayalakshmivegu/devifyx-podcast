import os
import re
import requests
from keybert import KeyBERT

def extract_keywords(text: str, num: int = 10):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, top_n=num)
    return [kw[0] for kw in keywords]

def extract_speakers(text):
    """Extract unique speaker labels like 'Speaker 1:' from the transcript."""
    speakers = set(re.findall(r'(Speaker \d+):', text))
    return list(speakers)

def process_transcript(content, language="en", summary_length=150):
    api_token = os.getenv("HF_API_TOKEN")
    headers = {"Authorization": f"Bearer {api_token}"}

    # Choose model based on language
    if language != "en":
        model = "facebook/mbart-large-50-many-to-many-mmt"
    else:
        model = "facebook/bart-large-cnn"

    payload = {
        "inputs": content,
        "parameters": {
            "max_length": summary_length,
            "min_length": max(20, summary_length // 3),
            "do_sample": False
        }
    }
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{model}",
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    summary = response.json()[0].get("summary_text", "")

    themes = extract_keywords(content, num=10)
    tags = [t.replace(" ", "-") for t in themes[:5]]
    speakers = extract_speakers(content)

    return {
        "summary": summary,
        "themes": themes,
        "tags": tags,
        "speakers": speakers
    }