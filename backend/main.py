from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from rule_engine import run_all_rules
try:
    from classifier import classify_text
    ML_AVAILABLE = True
except Exception as err:
    print("Classifier unavailable, using rule engine only:", err)
    ML_AVAILABLE = False

    def classify_text(text: str) -> dict:
        return {"detected": False, "category": "none", "confidence": 0.0}
from db_models import SessionLocal, Site, PatternType, LegalClause, Detection, Feedback

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    url: str
    dom_text: str
    dom_structure: Optional[List[Dict[str, Any]]] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan")
def scan(payload: ScanRequest):
    session = SessionLocal()

    rule_results = run_all_rules(payload.dom_text, payload.dom_structure)
    ml_result = classify_text(payload.dom_text)

    combined = {}
    for r in rule_results:
        combined[r["category"]] = r["confidence"]
    if ml_result["detected"]:
        cat = ml_result["category"]
        combined[cat] = max(combined.get(cat, 0), ml_result["confidence"])

    domain = payload.url
    site = session.query(Site).filter(Site.domain == domain).first()
    if not site:
        site = Site(domain=domain)
        session.add(site)
        session.commit()
        session.refresh(site)

    final_detections = []
    for category, confidence in combined.items():
        pattern_type = session.query(PatternType).filter(PatternType.category == category).first()
        clause_text = None
        law_name = None
        detection_id = None
        if pattern_type:
            clause = session.query(LegalClause).filter(LegalClause.pattern_type_id == pattern_type.id).first()
            if clause:
                clause_text = clause.clause_text
                law_name = clause.law_name

            detection = Detection(
                site_id=site.id,
                pattern_type_id=pattern_type.id,
                confidence_score=confidence,
                detected_text=payload.dom_text[:500],
            )
            session.add(detection)
            session.commit()
            session.refresh(detection)
            detection_id = detection.id

        final_detections.append({
            "category": category,
            "confidence": confidence,
            "law_name": law_name,
            "clause_text": clause_text,
            "detection_id": detection_id,
        })

    session.close()
    return {"url": payload.url, "detections": final_detections}


class FeedbackRequest(BaseModel):
    detection_id: int
    correct: bool
    comment: Optional[str] = None


@app.post("/feedback")
def feedback(payload: FeedbackRequest):
    session = SessionLocal()
    fb = Feedback(
        detection_id=payload.detection_id,
        correct=payload.correct,
        comment=payload.comment,
    )
    session.add(fb)
    session.commit()
    session.close()
    return {"status": "saved"}

SEVERITY = {
    "fake_urgency": 15,
    "subscription_trap": 20,
    "confirmshaming": 10,
    "preticked_checkbox": 15,
    "forced_continuity": 25,
    "scarcity_claim": 10,
}


@app.get("/report/{domain}")
def report(domain: str):
    session = SessionLocal()
    site = session.query(Site).filter(Site.domain == domain).first()
    if not site:
        session.close()
        return {"domain": domain, "trust_score": 100, "label": "No data yet", "scans": 0, "patterns": []}

    wrong_ids = {fb.detection_id for fb in session.query(Feedback).filter(Feedback.correct == False).all()}
    rows = (
        session.query(Detection, PatternType)
        .join(PatternType, Detection.pattern_type_id == PatternType.id)
        .filter(Detection.site_id == site.id)
        .all()
    )

    wrong_categories = {pt.category for det, pt in rows if det.id in wrong_ids}

    best = {}
    for det, pt in rows:
        if pt.category in wrong_categories:
            continue
        best[pt.category] = max(best.get(pt.category, 0), det.confidence_score or 0)

    penalty = sum(SEVERITY.get(cat, 10) * conf for cat, conf in best.items())
    score = max(0, round(100 - penalty))
    if score >= 80:
        label = "Good"
    elif score >= 50:
        label = "Caution"
    else:
        label = "Poor"

    session.close()
    return {
        "domain": domain,
        "trust_score": score,
        "label": label,
        "scans": len(rows),
        "patterns": [{"category": c, "max_confidence": round(v, 2)} for c, v in best.items()],
    }