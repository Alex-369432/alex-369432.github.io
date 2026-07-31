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

  // Копирование готового текста сообщения по кнопке [data-copy].
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = document.querySelector(btn.getAttribute("data-copy"));
      if (!target) return;
      var text = target.textContent.trim();
      var done = function () {
        var old = btn.textContent;
        btn.textContent = "Скопировано ✓";
        setTimeout(function () { btn.textContent = old; }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text, done); });
      } else {
        fallbackCopy(text, done);
      }
    });
  });

  function fallbackCopy(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); done(); } catch (e) {}
    document.body.removeChild(ta);
  }

  // Цели Метрики: клики по мессенджерам/звонку — считаем отдельно по каждому каналу.
  var YM_COUNTER_ID = 61801342;
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (!a || !a.href) return;
    var href = a.href;
    var goal = null;
    if (href.indexOf("wa.me") !== -1) goal = "click_whatsapp";
    else if (href.indexOf("t.me") !== -1) goal = "click_telegram";
    else if (href.indexOf("max.ru") !== -1) goal = "click_max";
    else if (href.indexOf("vk.ru") !== -1 || href.indexOf("vk.com") !== -1) goal = "click_vk";
    else if (href.indexOf("instagram.com") !== -1) goal = "click_instagram";
    else if (href.indexOf("sms:") === 0) goal = "click_sms";
    else if (href.indexOf("tel:") === 0) goal = "click_phone";
    if (goal && typeof ym === "function") ym(YM_COUNTER_ID, "reachGoal", goal);
  });
})();
