(function () {
  "use strict";

  // Мобильное меню
  var toggle = document.querySelector(".nav-toggle");
  var mobileNav = document.querySelector(".mobile-nav");
  if (toggle && mobileNav) {
    toggle.addEventListener("click", function () {
      var isOpen = mobileNav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
  }

  // FAQ-аккордеон (работает без JS тоже: контент присутствует в DOM,
  // JS только переключает видимость для UX)
  document.querySelectorAll(".faq-q").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var expanded = btn.getAttribute("aria-expanded") === "true";
      var answer = document.getElementById(btn.getAttribute("aria-controls"));
      btn.setAttribute("aria-expanded", expanded ? "false" : "true");
      if (answer) answer.setAttribute("data-open", expanded ? "false" : "true");
    });
  });

  // Открыть первый FAQ-блок на каждой странице по умолчанию для UX
  var firstFaq = document.querySelector(".faq-q");
  if (firstFaq) firstFaq.click();
})();
