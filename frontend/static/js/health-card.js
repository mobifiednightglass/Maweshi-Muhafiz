(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const animalId = new URLSearchParams(window.location.search).get('id');

  const copy = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں', logout: 'لاگ آؤٹ', backToPassport: 'صحت پاسپورٹ پر واپس جائیں',
      share: 'شیئر کریں', printSavePdf: 'پرنٹ / PDF محفوظ کریں', tryAgain: 'دوبارہ کوشش کریں', loadingLabel: 'ہیلتھ کارڈ دیکھا جا رہا ہے',
      missingTitle: 'جانور منتخب نہیں کیا گیا', missingMessage: 'ہیلتھ کارڈ دیکھنے کے لیے درست جانور منتخب کریں۔', notFoundTitle: 'ہیلتھ کارڈ نہیں ملا', notFoundMessage: 'یہ جانور موجود نہیں یا آپ کے ریکارڈ میں دستیاب نہیں۔',
      forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ ہیلتھ کارڈ دیکھنے کی اجازت نہیں ہے۔', connectionTitle: 'ہیلتھ کارڈ ابھی دستیاب نہیں', connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔', malformedTitle: 'ہیلتھ کارڈ مکمل نہیں', malformedMessage: 'اس کارڈ کی مکمل معلومات ابھی نہیں دکھائی جا سکتیں۔',
      buyerSummary: 'خریدار کے لیے آسان صحت خلاصہ', healthCardTitle: 'جانور کا ہیلتھ کارڈ', generatedOn: 'تیار کیا گیا', animal: 'جانور', notRecorded: 'درج نہیں',
      careRecord: 'دیکھ بھال کی یاددہانیاں', preventiveCare: 'بیماری سے بچاؤ کی دیکھ بھال', vaccination: 'ویکسین کی یاددہانی', deworming: 'کیڑے مار دوا کی یاددہانی', otherCare: 'دوسری یاددہانیاں', noOtherCare: 'کوئی دوسری یاددہانی درج نہیں۔',
      dueDate: 'مقررہ تاریخ', overdueBy: 'کتنے دن گزرے', daysOverdue: '{count} دن گزر گئے', upToDate: 'کوئی یاددہانی تاخیر کا شکار نہیں', attentionNeeded: 'توجہ درکار', unknown: 'درج نہیں', overdue: 'تاریخ گزر چکی ہے', notRecordedStatus: 'درج نہیں',
      reminderDisclaimer: 'یہ حیثیت محفوظ یاددہانی کی تاریخوں پر مبنی ہے؛ اس سے علاج مکمل ہونے کی تصدیق نہیں ہوتی۔', latestHealthCheck: 'تازہ ترین صحت معائنہ', urgency: 'فوری توجہ', lastAssessed: 'آخری معائنہ',
      noActiveWarning: 'کوئی فعال صحت تنبیہ نہیں', noActiveWarningMessage: 'تازہ ترین دستیاب معائنے میں فعال تنبیہ درج نہیں۔', activeWarning: 'فعال صحت تنبیہ موجود ہے', activeWarningMessage: 'تازہ ترین معائنے میں توجہ کی ضرورت درج ہے۔', noAssessmentWarning: 'صحت تنبیہ درج نہیں', noAssessmentWarningMessage: 'ابھی صحت معائنے کی معلومات دستیاب نہیں۔',
      urgencyLow: 'کم فوری توجہ', urgencyMedium: 'توجہ درکار', urgencyHigh: 'فوری توجہ', urgencyUnknown: 'درج نہیں', simplifiedRecord: 'یہ آسان صحت کارڈ ہے۔ مکمل ذاتی صحت ریکارڈ کسان کے پاس محفوظ رہتا ہے۔',
      shared: 'ہیلتھ کارڈ شیئر کر دیا گیا۔', shareUnavailable: 'اس براؤزر میں براہ راست شیئر دستیاب نہیں۔ پرنٹ / PDF محفوظ کریں اور محفوظ فائل شیئر کریں۔', shareFailed: 'ہیلتھ کارڈ شیئر نہیں ہو سکا۔ دوبارہ کوشش کریں۔'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language', logout: 'Logout', backToPassport: 'Back to Health Passport',
      share: 'Share', printSavePdf: 'Print / Save as PDF', tryAgain: 'Try again', loadingLabel: 'Loading Health Card',
      missingTitle: 'No animal selected', missingMessage: 'Select a valid animal to view its Health Card.', notFoundTitle: 'Health Card not found', notFoundMessage: 'This animal does not exist or is not available in your records.',
      forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to view this Health Card.', connectionTitle: 'Health Card unavailable right now', connectionMessage: 'We could not connect. Please try again in a little while.', malformedTitle: 'Health Card is incomplete', malformedMessage: 'Complete information for this card cannot be shown right now.',
      buyerSummary: 'A simple health summary for buyers', healthCardTitle: 'Animal Health Card', generatedOn: 'Generated', animal: 'Animal', notRecorded: 'Not recorded',
      careRecord: 'Care reminders', preventiveCare: 'Preventive Care', vaccination: 'Vaccination reminder', deworming: 'Deworming reminder', otherCare: 'Other reminders', noOtherCare: 'No other reminders recorded.',
      dueDate: 'Due date', overdueBy: 'Overdue by', daysOverdue: '{count} days overdue', upToDate: 'No reminder is overdue', attentionNeeded: 'Attention needed', unknown: 'Not recorded', overdue: 'Reminder date has passed', notRecordedStatus: 'Not recorded',
      reminderDisclaimer: 'These statuses are based on saved reminder dates; they do not confirm that care or treatment was completed.', latestHealthCheck: 'Latest health assessment', urgency: 'Urgency', lastAssessed: 'Last assessed',
      noActiveWarning: 'No active health warning', noActiveWarningMessage: 'No active warning is recorded in the latest available assessment.', activeWarning: 'Active health warning', activeWarningMessage: 'The latest assessment indicates that attention may be needed.', noAssessmentWarning: 'Health warning not recorded', noAssessmentWarningMessage: 'Health-assessment information is not available yet.',
      urgencyLow: 'Low urgency', urgencyMedium: 'Needs attention', urgencyHigh: 'Urgent attention', urgencyUnknown: 'Not recorded', simplifiedRecord: 'This is a simplified Health Card. The farmer retains the full private health record.',
      shared: 'Health Card shared.', shareUnavailable: 'Direct sharing is not available in this browser. Use Print / Save as PDF and share the saved file.', shareFailed: 'The Health Card could not be shared. Please try again.'
    }
  };

  const el = {
    loading: document.querySelector('#health-card-loading'), error: document.querySelector('#health-card-error'), page: document.querySelector('#health-card-page'), actions: document.querySelector('#card-actions'),
    errorTitle: document.querySelector('#health-card-error-title'), errorMessage: document.querySelector('#health-card-error-message'), retry: document.querySelector('#retry-card'), passportLink: document.querySelector('#passport-link'), errorPassportLink: document.querySelector('#error-passport-link'),
    share: document.querySelector('#share-card'), print: document.querySelector('#print-card'), feedback: document.querySelector('#share-feedback'), generated: document.querySelector('#generated-date'),
    animalIcon: document.querySelector('#animal-icon'), animalName: document.querySelector('#animal-name'), animalType: document.querySelector('#animal-type'), preventiveOverall: document.querySelector('#preventive-overall'),
    vaccinationStatus: document.querySelector('#vaccination-status'), vaccinationDate: document.querySelector('#vaccination-date'), vaccinationOverdueRow: document.querySelector('#vaccination-overdue-row'), vaccinationOverdue: document.querySelector('#vaccination-overdue'),
    dewormingStatus: document.querySelector('#deworming-status'), dewormingDate: document.querySelector('#deworming-date'), dewormingOverdueRow: document.querySelector('#deworming-overdue-row'), dewormingOverdue: document.querySelector('#deworming-overdue'),
    otherCare: document.querySelector('#other-care-list'), otherCareEmpty: document.querySelector('#other-care-empty'), warning: document.querySelector('#warning-section'), warningIcon: document.querySelector('#warning-icon'), warningTitle: document.querySelector('#warning-heading'), warningDescription: document.querySelector('#warning-description'), warningUrgency: document.querySelector('#warning-urgency'), lastAssessed: document.querySelector('#last-assessed')
  };

  let language = window.MaweshiI18n.getLanguage();
  let card = null;
  let errorKind = null;
  let feedbackKey = null;
  let feedbackIsError = false;

  function t(key, values = {}) {
    let value = copy[language][key] || key;
    Object.entries(values).forEach(([name, replacement]) => { value = value.replace(`{${name}}`, replacement); });
    return value;
  }

  function text(value, fallback = t('notRecorded')) {
    return value === null || value === undefined || String(value).trim() === '' ? fallback : String(value);
  }

  function reminderTypeLabel(value) {
    return window.MaweshiI18n.reminderTypeLabel(value, language);
  }

  function formatDate(raw) {
    if (!raw) return t('notRecorded');
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) return t('notRecorded');
    return new Intl.DateTimeFormat(language === 'ur' ? 'ur-PK' : 'en-PK', { day: 'numeric', month: 'short', year: 'numeric' }).format(date);
  }

  function animalIcon(type) {
    const normalized = text(type, '').toLowerCase();
    if (normalized.includes('buffalo') || normalized.includes('بھینس')) return '🐃';
    if (normalized.includes('goat') || normalized.includes('بکری') || normalized.includes('بکرا')) return '🐐';
    if (normalized.includes('sheep') || normalized.includes('بھیڑ') || normalized.includes('دنبہ')) return '🐑';
    if (normalized.includes('cow') || normalized.includes('cattle') || normalized.includes('گائے') || normalized.includes('بیل')) return '🐄';
    return '🐾';
  }

  function statusText(status) {
    if (status === 'up_to_date') return t('upToDate');
    if (status === 'attention_needed') return t('attentionNeeded');
    if (status === 'overdue') return t('overdue');
    return t(status === 'not_recorded' ? 'notRecordedStatus' : 'unknown');
  }

  function statusClass(status) {
    if (status === 'up_to_date') return 'status-good';
    if (status === 'attention_needed' || status === 'overdue') return 'status-warning';
    return 'status-neutral';
  }

  function urgencyText(level) {
    return t(level === 'high' ? 'urgencyHigh' : level === 'medium' ? 'urgencyMedium' : level === 'low' ? 'urgencyLow' : 'urgencyUnknown');
  }

  function isCategory(value) {
    return value && typeof value === 'object' && !Array.isArray(value);
  }

  function isCard(value) {
    return value && typeof value === 'object' && !Array.isArray(value)
      && value.animal && typeof value.animal === 'object' && !Array.isArray(value.animal)
      && value.preventive_care && typeof value.preventive_care === 'object' && !Array.isArray(value.preventive_care)
      && value.health_warnings && typeof value.health_warnings === 'object' && !Array.isArray(value.health_warnings);
  }

  function setLinks() {
    const destination = animalId ? `health-passport.html?id=${encodeURIComponent(animalId)}` : 'dashboard.html';
    el.passportLink.href = destination;
    el.errorPassportLink.href = destination;
  }

  function renderCategory(category, statusNode, dateNode, overdueRow, overdueNode) {
    const value = isCategory(category) ? category : {};
    statusNode.textContent = statusText(value.status);
    statusNode.className = `care-status-text ${statusClass(value.status)}`;
    dateNode.textContent = formatDate(value.due_date);
    const days = Number(value.days_overdue);
    const hasDays = value.status === 'overdue' && Number.isFinite(days) && days >= 0;
    overdueRow.classList.toggle('hidden', !hasDays);
    overdueNode.textContent = hasDays ? t('daysOverdue', { count: new Intl.NumberFormat(language === 'ur' ? 'ur-PK' : 'en-PK').format(days) }) : '';
  }

  function renderOtherCare(records) {
    const list = Array.isArray(records) ? records.filter(isCategory) : [];
    el.otherCare.replaceChildren();
    el.otherCareEmpty.classList.toggle('hidden', list.length !== 0);
    list.forEach((record) => {
      const article = document.createElement('article');
      article.className = 'other-care-record';
      const name = document.createElement('strong');
      name.dir = 'auto';
      name.textContent = reminderTypeLabel(record.reminder_type) || t('notRecorded');
      const status = document.createElement('span');
      status.className = `other-care-status ${statusClass(record.status)}`;
      status.textContent = statusText(record.status);
      const due = document.createElement('time');
      due.dateTime = record.due_date || '';
      due.textContent = `${t('dueDate')}: ${formatDate(record.due_date)}`;
      article.append(name, status, due);
      if (record.status === 'overdue' && Number.isFinite(Number(record.days_overdue))) {
        const days = document.createElement('span');
        days.className = 'other-care-status status-warning';
        days.textContent = t('daysOverdue', { count: new Intl.NumberFormat(language === 'ur' ? 'ur-PK' : 'en-PK').format(Number(record.days_overdue)) });
        article.appendChild(days);
      }
      el.otherCare.appendChild(article);
    });
  }

  function renderWarning(warning) {
    const hasWarning = warning.has_active_warning === true;
    const level = ['low', 'medium', 'high'].includes(warning.urgency_level) ? warning.urgency_level : null;
    let visual = hasWarning ? level || 'unknown' : warning.last_assessed_at ? 'low' : 'unknown';
    el.warning.className = `warning-section is-${visual}`;
    el.warningIcon.textContent = hasWarning ? '!' : warning.last_assessed_at ? '✓' : '—';
    el.warningTitle.textContent = hasWarning ? t('activeWarning') : warning.last_assessed_at ? t('noActiveWarning') : t('noAssessmentWarning');
    el.warningDescription.textContent = hasWarning ? t('activeWarningMessage') : warning.last_assessed_at ? t('noActiveWarningMessage') : t('noAssessmentWarningMessage');
    el.warningUrgency.textContent = urgencyText(level);
    el.lastAssessed.textContent = formatDate(warning.last_assessed_at);
  }

  function renderCard() {
    if (!card) return;
    const animal = card.animal;
    const care = card.preventive_care;
    el.generated.textContent = formatDate(card.generated_at);
    el.animalIcon.textContent = animalIcon(animal.animal_type);
    el.animalName.textContent = text(animal.name);
    el.animalType.textContent = text(animal.animal_type);
    el.preventiveOverall.className = `card-status ${statusClass(care.status)}`;
    el.preventiveOverall.textContent = statusText(care.status);
    renderCategory(care.vaccination, el.vaccinationStatus, el.vaccinationDate, el.vaccinationOverdueRow, el.vaccinationOverdue);
    renderCategory(care.deworming, el.dewormingStatus, el.dewormingDate, el.dewormingOverdueRow, el.dewormingOverdue);
    renderOtherCare(care.other);
    renderWarning(card.health_warnings);
    document.title = `${text(animal.name)} | ${t('healthCardTitle')} | Maweshi Muhafiz`;
  }

  function showError(kind) {
    errorKind = kind;
    el.loading.classList.add('hidden');
    el.page.classList.add('hidden');
    el.actions.classList.add('hidden');
    el.error.classList.remove('hidden');
    el.errorTitle.textContent = t(`${kind}Title`);
    el.errorMessage.textContent = t(`${kind}Message`);
    el.retry.classList.toggle('hidden', kind === 'missing' || kind === 'notFound');
  }

  async function loadCard() {
    card = null;
    errorKind = null;
    el.error.classList.add('hidden');
    el.page.classList.add('hidden');
    el.actions.classList.add('hidden');
    el.loading.classList.remove('hidden');
    if (!animalId || !animalId.trim()) { showError('missing'); return; }
    try {
      const data = await window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(animalId)}/health-card`, { headers: { Accept: 'application/json' } });
      if (!isCard(data)) { showError('malformed'); return; }
      card = data;
      renderCard();
      el.loading.classList.add('hidden');
      el.page.classList.remove('hidden');
      el.actions.classList.remove('hidden');
    } catch (error) {
      console.error('Health Card could not be loaded.', error);
      showError(error.status === 404 ? 'notFound' : error.status === 403 ? 'forbidden' : 'connection');
    }
  }

  function setFeedback(key, isError = false) {
    feedbackKey = key;
    feedbackIsError = isError;
    el.feedback.textContent = t(key);
    el.feedback.classList.toggle('is-error', isError);
    el.feedback.classList.remove('hidden');
  }

  function categoryShare(label, category) {
    const value = isCategory(category) ? category : {};
    const due = value.due_date ? ` · ${t('dueDate')}: ${formatDate(value.due_date)}` : '';
    return `${label}: ${statusText(value.status)}${due}`;
  }

  function shareText() {
    const warning = card.health_warnings;
    const warningText = warning.has_active_warning === true
      ? `${t('activeWarning')} · ${urgencyText(warning.urgency_level)}`
      : warning.last_assessed_at ? t('noActiveWarning') : t('noAssessmentWarning');
    return [
      `Maweshi Muhafiz — ${t('healthCardTitle')}`,
      `${t('animal')}: ${text(card.animal.name)} · ${text(card.animal.animal_type)}`,
      `${t('preventiveCare')}: ${statusText(card.preventive_care.status)}`,
      categoryShare(t('vaccination'), card.preventive_care.vaccination),
      categoryShare(t('deworming'), card.preventive_care.deworming),
      `${t('latestHealthCheck')}: ${warningText}`,
      `${t('generatedOn')}: ${formatDate(card.generated_at)}`
    ].join('\n');
  }

  async function shareCard() {
    if (!card) return;
    if (!navigator.share) { setFeedback('shareUnavailable'); return; }
    try {
      await navigator.share({ title: t('healthCardTitle'), text: shareText() });
      setFeedback('shared');
    } catch (error) {
      if (error?.name === 'AbortError') return;
      console.error('Health Card could not be shared.', error);
      setFeedback('shareFailed', true);
    }
  }

  function applyLanguage(nextLanguage) {
    language = window.MaweshiI18n.applyPage(nextLanguage, copy).language;
    if (card) renderCard();
    if (errorKind) showError(errorKind);
    if (feedbackKey) setFeedback(feedbackKey, feedbackIsError);
  }

  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) applyLanguage(languageButton.dataset.language);
  });
  el.retry.addEventListener('click', loadCard);
  el.print.addEventListener('click', () => window.print());
  el.share.addEventListener('click', shareCard);

  setLinks();
  applyLanguage(language);
  loadCard();
})();
