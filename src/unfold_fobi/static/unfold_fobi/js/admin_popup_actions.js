(function () {
  "use strict";

  function onReady(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
      return;
    }
    callback();
  }

  function decoratePopupLinks(root) {
    const links = (root || document).querySelectorAll(
      "a[data-popup='yes'][id^='add_fobi_element_'], a[data-popup='yes'][id^='add_fobi_handler_']"
    );
    links.forEach(function (link) {
      link.classList.add("related-widget-wrapper-link");
    });
  }

  onReady(function () {
    // Make native Unfold dropdown links follow the same selector contract
    // as Django related widgets, then reuse stock admin/unfold_modal handlers.
    decoratePopupLinks(document);

    // Keep class assignment for any links inserted later.
    const observer = new MutationObserver(function (records) {
      records.forEach(function (record) {
        record.addedNodes.forEach(function (node) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            decoratePopupLinks(node);
          }
        });
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });
})();
