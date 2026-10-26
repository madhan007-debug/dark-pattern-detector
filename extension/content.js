"use strict";
function extractPageText() {
    return document.body.innerText.slice(0, 3000);
}
function extractDomStructure() {
    const elements = [];
    document.querySelectorAll('input[type="checkbox"]').forEach((el) => {
        const input = el;
        const parentText = input.closest("label, div, li")?.textContent || "";
        elements.push({
            tag: "input",
            type: "checkbox",
            checked: input.checked,
            nearby_text: parentText.slice(0, 200),
        });
    });
    document.querySelectorAll("a, button").forEach((el) => {
        const text = el.textContent || "";
        if (text.toLowerCase().includes("cancel")) {
            const style = window.getComputedStyle(el);
            elements.push({
                tag: "a",
                text: text.trim(),
                font_size: parseInt(style.fontSize) || 12,
                clicks_deep: 1,
            });
        }
    });
    return elements;
}
let scanTimer;
function sendScan() {
    const payload = {
        url: window.location.hostname,
        dom_text: extractPageText(),
        dom_structure: extractDomStructure(),
    };
    chrome.runtime.sendMessage({ type: "SCAN_PAGE", payload: payload });
}
function scheduleScan() {
    clearTimeout(scanTimer);
    scanTimer = window.setTimeout(sendScan, 1500);
}
scheduleScan();
new MutationObserver(scheduleScan).observe(document.body, {
    childList: true,
    subtree: true,
});
//# sourceMappingURL=content.js.map