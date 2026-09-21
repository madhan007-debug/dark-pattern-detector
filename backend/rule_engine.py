import re

def detect_fake_urgency(text: str) -> dict:
    """Category 1: countdown timers, urgency phrases"""
    timer_pattern = r'\b\d{1,2}:\d{2}(:\d{2})?\b'
    urgency_words = r'(hurry|ends soon|limited time|offer expires|only today|act now)'
    if re.search(timer_pattern, text) or re.search(urgency_words, text, re.IGNORECASE):
        return {"detected": True, "category": "fake_urgency", "confidence": 0.8}
    return {"detected": False, "category": "fake_urgency", "confidence": 0.0}


def detect_subscription_trap(text: str) -> dict:
    """Category 2: hidden subscription / auto-renewal wording"""
    pattern = r'(auto[\s-]?renew|subscription will continue|cancel anytime\*|free trial.*then charged)'
    if re.search(pattern, text, re.IGNORECASE):
        return {"detected": True, "category": "subscription_trap", "confidence": 0.75}
    return {"detected": False, "category": "subscription_trap", "confidence": 0.0}


def detect_confirmshaming(text: str) -> dict:
    """Category 3: guilt-tripping decline options"""
    pattern = r"(no,? i.*(don't|do not) (want|like)|no thanks.*(miss|regret)|no,? i prefer to (pay|struggle))"
    if re.search(pattern, text, re.IGNORECASE):
        return {"detected": True, "category": "confirmshaming", "confidence": 0.75}
    return {"detected": False, "category": "confirmshaming", "confidence": 0.0}


def detect_preticked_checkbox(dom_structure: list) -> dict:
    """Category 4: pre-selected consent/add-on checkboxes"""
    keywords = r'(newsletter|protection plan|insurance|subscribe|add.?on)'
    for el in dom_structure:
        if el.get("tag") == "input" and el.get("type") == "checkbox" and el.get("checked"):
            if re.search(keywords, el.get("nearby_text", ""), re.IGNORECASE):
                return {"detected": True, "category": "preticked_checkbox", "confidence": 0.85}
    return {"detected": False, "category": "preticked_checkbox", "confidence": 0.0}


def detect_forced_continuity(dom_structure: list) -> dict:
    """Category 5: hard-to-cancel flows"""
    for el in dom_structure:
        text = el.get("text", "").lower()
        if "cancel" in text and ("subscription" in text or "membership" in text):
            if el.get("font_size", 12) < 10 or el.get("clicks_deep", 1) > 2:
                return {"detected": True, "category": "forced_continuity", "confidence": 0.7}
    return {"detected": False, "category": "forced_continuity", "confidence": 0.0}


def detect_scarcity_claim(text: str) -> dict:
    """Category 6: fake low-stock / high-demand messages"""
    pattern = r'\bonly \d+ (left|remaining)\b|\d+ people (are )?(viewing|bought|added)'
    if re.search(pattern, text, re.IGNORECASE):
        return {"detected": True, "category": "scarcity_claim", "confidence": 0.75}
    return {"detected": False, "category": "scarcity_claim", "confidence": 0.0}


def run_all_rules(text: str, dom_structure: list = None) -> list:
    """Runs all 6 detectors and returns only the ones that fired"""
    if dom_structure is None:
        dom_structure = []
    results = [
        detect_fake_urgency(text),
        detect_subscription_trap(text),
        detect_confirmshaming(text),
        detect_preticked_checkbox(dom_structure),
        detect_forced_continuity(dom_structure),
        detect_scarcity_claim(text),
    ]
    return [r for r in results if r["detected"]]


if __name__ == "__main__":
    sample_text = "Hurry! Offer ends in 05:32. Only 3 left in stock. Free trial, then charged automatically."
    sample_dom = [
        {"tag": "input", "type": "checkbox", "checked": True, "nearby_text": "Add protection plan"},
        {"tag": "a", "text": "cancel subscription", "font_size": 8, "clicks_deep": 3}
    ]
    print(run_all_rules(sample_text, sample_dom))