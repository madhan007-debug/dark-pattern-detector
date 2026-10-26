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
//# sourceMappingURL=popup.d.ts.map