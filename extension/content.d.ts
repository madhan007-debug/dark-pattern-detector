interface DomElement {
    tag: string;
    type?: string;
    checked?: boolean;
    nearby_text?: string;
    text?: string;
    font_size?: number;
    clicks_deep?: number;
}
declare function extractPageText(): string;
declare function extractDomStructure(): DomElement[];
declare let scanTimer: number | undefined;
declare function sendScan(): void;
declare function scheduleScan(): void;
//# sourceMappingURL=content.d.ts.map