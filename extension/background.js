"use strict";
chrome.runtime.onInstalled.addListener(() => {
    console.log("Dark Pattern Detector installed");
});
chrome.runtime.onMessage.addListener((message, sender) => {
    if (message.type !== "SCAN_PAGE" || !sender.tab || sender.tab.id === undefined) {
        return;
    }
    const tabId = sender.tab.id;
    fetch("http://localhost:8000/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(message.payload),
    })
        .then((response) => response.json())
        .then((data) => {
        chrome.storage.local.set({ ["scan_" + tabId]: data });
        const count = data.detections ? data.detections.length : 0;
        chrome.action.setBadgeText({ text: count > 0 ? String(count) : "", tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: "#e63946", tabId: tabId });
    })
        .catch((err) => console.error("Dark Pattern Detector scan failed:", err));
});
//# sourceMappingURL=background.js.map