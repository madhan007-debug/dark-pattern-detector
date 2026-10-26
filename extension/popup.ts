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

chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  const resultsDiv = document.getElementById("results")!;
  const tab = tabs[0];

  if (!tab || tab.id === undefined) {
    resultsDiv.innerHTML = '<div class="none">Cannot read this tab.</div>';
    return;
  }

  const key = "scan_" + tab.id;
  chrome.storage.local.get(key, (data) => {
    const scan = data[key] as ScanResult | undefined;

    if (!scan) {
      resultsDiv.innerHTML =
        '<div class="none">No scan result for this page yet. Refresh the page and wait a few seconds.</div>';
      return;
    }

    if (scan.detections.length === 0) {
      resultsDiv.innerHTML =
        '<div class="none">No dark patterns detected on ' + scan.url + ".</div>";
      return;
    }

    resultsDiv.innerHTML = "<div class='confidence'>Results for " + scan.url + "</div>";
    scan.detections.forEach((d) => {
      const div = document.createElement("div");
      div.className = "detection";
      div.innerHTML = `
        <div class="category">${d.category.replace(/_/g, " ")}</div>
        <div class="confidence">Confidence: ${(d.confidence * 100).toFixed(0)}%</div>
        ${d.clause_text ? `<div class="clause">${d.clause_text}</div>` : ""}
        ${d.law_name ? `<div class="law">— ${d.law_name}</div>` : ""}
        <div style="margin-top:6px;font-size:12px;">
          <button class="fb-yes">Correct</button>
          <button class="fb-no">This wasn't right</button>
          <span class="fb-msg" style="margin-left:6px;color:#2a9d8f;"></span>
        </div>
      `;

      const msg = div.querySelector(".fb-msg") as HTMLElement;
      const send = (correct: boolean) => {
        if (d.detection_id === null) {
          return;
        }
        fetch("http://localhost:8000/feedback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ detection_id: d.detection_id, correct: correct }),
        })
          .then(() => {
            msg.textContent = "Thanks, saved";
          })
          .catch(() => {
            msg.textContent = "Could not save";
          });
      };
      (div.querySelector(".fb-yes") as HTMLElement).onclick = () => send(true);
      (div.querySelector(".fb-no") as HTMLElement).onclick = () => send(false);

      resultsDiv.appendChild(div);
    });
  });
});