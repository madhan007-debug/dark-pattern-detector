chrome.storage.local.get("lastScan", (data) => {
    const resultsDiv = document.getElementById("results");
    if (!data.lastScan || data.lastScan.detections.length === 0) {
        resultsDiv.innerHTML = '<div class="none">No dark patterns detected on this page.</div>';
        return;
    }
    resultsDiv.innerHTML = "";
    data.lastScan.detections.forEach((d) => {
        const div = document.createElement("div");
        div.className = "detection";
        div.innerHTML = `
      <div class="category">${d.category.replace(/_/g, " ")}</div>
      <div class="confidence">Confidence: ${(d.confidence * 100).toFixed(0)}%</div>
      ${d.clause_text ? `<div class="clause">${d.clause_text}</div>` : ""}
      ${d.law_name ? `<div class="law">— ${d.law_name}</div>` : ""}
    `;
        resultsDiv.appendChild(div);
    });
});
export {};
//# sourceMappingURL=popup.js.map