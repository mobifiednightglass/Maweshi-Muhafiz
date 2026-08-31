(() => {
  'use strict';

  const STORAGE_KEY = 'maweshi-language';
  const SUPPORTED = new Set(['ur', 'en']);

  function getLanguage() {
    const saved = localStorage.getItem(STORAGE_KEY);
    return SUPPORTED.has(saved) ? saved : 'ur';
  }

  function setLanguage(language) {
    const next = SUPPORTED.has(language) ? language : 'ur';
    localStorage.setItem(STORAGE_KEY, next);
    document.documentElement.lang = next;
    document.documentElement.dir = next === 'ur' ? 'rtl' : 'ltr';
    return next;
  }

  function applyPage(language, messages, root = document) {
    const active = setLanguage(language);
    const dictionary = messages[active] || messages.ur || {};
    const translate = (key) => dictionary[key] || key;

    root.querySelectorAll('[data-i18n]').forEach((node) => { node.textContent = translate(node.dataset.i18n); });
    root.querySelectorAll('[data-i18n-placeholder]').forEach((node) => { node.placeholder = translate(node.dataset.i18nPlaceholder); });
    root.querySelectorAll('[data-i18n-aria-label]').forEach((node) => { node.setAttribute('aria-label', translate(node.dataset.i18nAriaLabel)); });
    root.querySelectorAll('[data-language]').forEach((button) => {
      const selected = button.dataset.language === active;
      button.classList.toggle('is-active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });

    return { language: active, t: translate };
  }

  window.MaweshiI18n = { applyPage, getLanguage, setLanguage };
})();
