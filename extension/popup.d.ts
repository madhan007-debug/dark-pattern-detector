interface Detection {
    category: string;
    confidence: number;
    law_name: string | null;
    clause_text: string | null;
    detection_id: number | null;
}
interface ScanResult {
    url: string;
    detections: Detection[];
}
interface Report {
    domain: string;
    trust_score: number;
    label: string;
    scans: number;
}
declare function trustColor(score: number): string;
declare function addTrustBadge(container: HTMLElement, domain: string): void;
//# sourceMappingURL=popup.d.ts.map