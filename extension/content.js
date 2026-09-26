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
async function scanPage() {
    const payload = {
        url: window.location.hostname,
        dom_text: extractPageText(),
        dom_structure: extractDomStructure(),
    };
    try {
        const response = await fetch("http://localhost:8000/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        chrome.storage.local.set({ lastScan: data });
    }
    catch (err) {
        console.error("Dark Pattern Detector scan failed:", err);
    }
}
scanPage();
const observer = new MutationObserver(() => {
    scanPage();
});
observer.observe(document.body, { childList: true, subtree: true });
export {};
//# sourceMappingURL=content.js.map