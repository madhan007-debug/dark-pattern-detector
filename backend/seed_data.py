from db_models import SessionLocal, PatternType, LegalClause, init_db

init_db()
session = SessionLocal()

categories = [
    ("Fake Urgency", "fake_urgency", "Countdown timers and urgency phrases pressuring immediate purchase."),
    ("Subscription Trap", "subscription_trap", "Hidden auto-renewal or subscription continuation wording."),
    ("Confirmshaming", "confirmshaming", "Guilt-tripping language on decline/opt-out options."),
    ("Pre-ticked Checkbox", "preticked_checkbox", "Pre-selected consent or add-on checkboxes."),
    ("Forced Continuity", "forced_continuity", "Deliberately difficult cancellation flows."),
    ("Scarcity Claim", "scarcity_claim", "Fake or exaggerated low-stock / high-demand messaging."),
]

clauses = {
    "fake_urgency": ("FTC Dark Patterns Guidance 2022", "Deceptive urgency cues that misrepresent time-limited availability are considered unfair or deceptive practices."),
    "subscription_trap": ("India CCPA Guidelines 2023", "Subscription traps that make cancellation difficult or hide auto-renewal terms are prohibited dark patterns."),
    "confirmshaming": ("India CCPA Guidelines 2023", "Confirmshaming that uses guilt or shame to influence a consumer's choice is a recognized dark pattern."),
    "preticked_checkbox": ("EU Digital Services Act 2022", "Pre-selected options that add costs or services without explicit consent violate informed consent requirements."),
    "forced_continuity": ("FTC Click-to-Cancel Rule", "Cancellation must be at least as easy as the sign-up process; obstruction is a prohibited practice."),
    "scarcity_claim": ("India CCPA Guidelines 2023", "False or exaggerated scarcity claims that pressure purchase decisions are a recognized dark pattern."),
}

for name, category, description in categories:
    existing = session.query(PatternType).filter(PatternType.category == category).first()
    if not existing:
        pt = PatternType(name=name, category=category, description=description)
        session.add(pt)
        session.commit()
        session.refresh(pt)
        law_name, clause_text = clauses[category]
        lc = LegalClause(pattern_type_id=pt.id, law_name=law_name, clause_text=clause_text)
        session.add(lc)
        session.commit()

print("Seed data inserted.")
session.close()