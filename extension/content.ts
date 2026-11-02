interface DomElement {
  tag: string;
  type?: string;
  checked?: boolean;
  nearby_text?: string;
  text?: string;
  font_size?: number;
  clicks_deep?: number;
}

function extractPageText(): string {
  return document.body.innerText.slice(0, 3000);
}

function extractDomStructure(): DomElement[] {
  const elements: DomElement[] = [];

  document.querySelectorAll('input[type="checkbox"]').forEach((el) => {
    const input = el as HTMLInputElement;
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

let scanTimer: number | undefined;

function sendScan() {
  try {
    if (!chrome.runtime?.id) {
      observer.disconnect();
      return;
    }
    const payload = {
      url: window.location.hostname || "local-test-page",
      dom_text: extractPageText(),
      dom_structure: extractDomStructure(),
    };
    chrome.runtime.sendMessage({ type: "SCAN_PAGE", payload: payload });
  } catch (err) {
    observer.disconnect();
  }
}

function scheduleScan() {
  clearTimeout(scanTimer);
  scanTimer = window.setTimeout(sendScan, 1500);
}

const observer = new MutationObserver(scheduleScan);
observer.observe(document.body, { childList: true, subtree: true });
scheduleScan();