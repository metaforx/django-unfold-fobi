(function () {
  "use strict";

  function onReady(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
      return;
    }
    callback();
  }

  function isFobiAddPopupLink(link) {
    if (!link || link.dataset.popup !== "yes") {
      return false;
    }
    const id = link.id || "";
    return id.startsWith("add_fobi_element_") || id.startsWith("add_fobi_handler_");
  }

  function openRelatedPopup(link) {
    if (
      !window.django ||
      !django.jQuery ||
      typeof window.showRelatedObjectPopup !== "function"
    ) {
      return;
    }
    // unfold_modal delegates on ".related-widget-wrapper-link[data-popup='yes']".
    // Native Unfold action links don't have this class, so add it before trigger.
    link.classList.add("related-widget-wrapper-link");
    const $ = django.jQuery;
    const relatedEvent = $.Event("django:show-related", { href: link.href });
    $(link).trigger(relatedEvent);
    if (!relatedEvent.isDefaultPrevented()) {
      window.showRelatedObjectPopup(link);
    }
  }

  onReady(function () {
    document.body.addEventListener("click", function (event) {
      const link = event.target.closest("a[data-popup='yes']");
      if (!isFobiAddPopupLink(link)) {
        return;
      }
      event.preventDefault();
      openRelatedPopup(link);
    });
  });
})();
