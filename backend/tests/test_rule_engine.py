from rule_engine import (
    detect_fake_urgency, detect_subscription_trap, detect_confirmshaming,
    detect_preticked_checkbox, detect_forced_continuity, detect_scarcity_claim, run_all_rules,
)


def test_fake_urgency_detected():
    result = detect_fake_urgency("Hurry! Offer ends in 05:32")
    assert result["detected"] is True and result["category"] == "fake_urgency"


def test_fake_urgency_not_detected_on_plain_text():
    assert detect_fake_urgency("Welcome to our store")["detected"] is False


def test_subscription_trap_detected():
    assert detect_subscription_trap("Your free trial will auto-renew each month")["detected"] is True


def test_subscription_trap_not_detected_on_plain_text():
    assert detect_subscription_trap("Free returns within 30 days")["detected"] is False


def test_confirmshaming_detected():
    assert detect_confirmshaming("No, I don't want to save money")["detected"] is True


def test_confirmshaming_not_detected_on_plain_text():
    assert detect_confirmshaming("Add to cart")["detected"] is False


def test_preticked_checkbox_detected():
    dom = [{"tag": "input", "type": "checkbox", "checked": True, "nearby_text": "Add protection plan"}]
    assert detect_preticked_checkbox(dom)["detected"] is True


def test_unticked_checkbox_not_detected():
    dom = [{"tag": "input", "type": "checkbox", "checked": False, "nearby_text": "Add protection plan"}]
    assert detect_preticked_checkbox(dom)["detected"] is False


def test_forced_continuity_detected_for_tiny_cancel_link():
    dom = [{"tag": "a", "text": "cancel subscription", "font_size": 8, "clicks_deep": 3}]
    assert detect_forced_continuity(dom)["detected"] is True


def test_forced_continuity_not_detected_for_visible_cancel_link():
    dom = [{"tag": "a", "text": "cancel subscription", "font_size": 14, "clicks_deep": 1}]
    assert detect_forced_continuity(dom)["detected"] is False


def test_scarcity_claim_detected():
    assert detect_scarcity_claim("Only 3 left in stock")["detected"] is True


def test_scarcity_claim_not_detected_on_plain_text():
    assert detect_scarcity_claim("The store opens at 9 am")["detected"] is False


def test_run_all_rules_finds_all_five_categories_on_sample_page():
    text = "Hurry! Offer ends in 05:32. Only 3 left in stock. Free trial, then charged automatically."
    dom = [
        {"tag": "input", "type": "checkbox", "checked": True, "nearby_text": "Add protection plan"},
        {"tag": "a", "text": "cancel subscription", "font_size": 8, "clicks_deep": 3},
    ]
    found = {r["category"] for r in run_all_rules(text, dom)}
    assert found == {"fake_urgency", "subscription_trap", "preticked_checkbox", "forced_continuity", "scarcity_claim"}


def test_run_all_rules_returns_nothing_for_ordinary_text():
    assert run_all_rules("Photosynthesis is the process by which plants make food.", []) == []