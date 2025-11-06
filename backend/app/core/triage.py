import re
from typing import Tuple, List

KEYWORDS = {
    "phishing": ["verify", "password", "account", "bank", "login", "urgent", "suspended"],
    "scam": ["lottery", "prize", "gift", "win", "investment", "crypto", "airdrop"],
    "malware": ["attachment", "exe", "download", "apk", "infected", "trojan"],
}

def evaluate_text(text: str) -> Tuple[float, List[str]]:
    text_l = text.lower()
    score = 0
    reasons: List[str] = []
    for cat, words in KEYWORDS.items():
        hits = [w for w in words if w in text_l]
        if hits:
            reasons.append(f"{cat} indicators: {', '.join(hits)}")
            score += min(len(hits), 3)  # cap contribution per category
    # simple URL red flag
    url_hits = re.findall(r"https?://\S+", text_l)
    if url_hits:
        reasons.append(f"contains URL(s): {len(url_hits)}")
        score += 1
    score_norm = min(score / 6, 1.0)
    return score_norm, reasons