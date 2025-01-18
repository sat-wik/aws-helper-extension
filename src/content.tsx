chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.action === "highlight" && message.selector) {
    const elements = document.querySelectorAll(message.selector);
    elements.forEach((el) => {
      (el as HTMLElement).style.outline = "2px solid red";
    });
    sendResponse({ success: true });
  }
});
