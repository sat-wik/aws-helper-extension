chrome.runtime.onMessage.addListener((e,o,t)=>{e.action==="highlight"&&e.selector&&(document.querySelectorAll(e.selector).forEach(l=>{l.style.outline="2px solid red"}),t({success:!0}))});
