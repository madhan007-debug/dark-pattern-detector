from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from rule_engine import run_all_rules
from classifier import classify_text
from db_models import SessionLocal, Site, PatternType, LegalClause, Detection

app = FastAPI()


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