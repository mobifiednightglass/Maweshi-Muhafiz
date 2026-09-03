(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const animalId = new URLSearchParams(window.location.search).get('id');

  const copy = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں', logout: 'لاگ آؤٹ', backToProfile: 'جانور کے پروفائل پر واپس جائیں',
      loadingLabel: 'صحت کی پچھلی تفصیل دیکھی جا رہی ہے', historyTitle: 'صحت کی پچھلی تفصیل', historySubtitle: 'اس جانور کے پچھلے صحت معائنے ایک جگہ دیکھیں۔',
      noAssessments: 'ابھی تک صحت کا کوئی معائنہ موجود نہیں ہے۔', emptyHelp: 'پہلا معائنہ شروع کرنے کے لیے جانور کے پروفائل پر جائیں۔', startAssessment: 'صحت کا معائنہ شروع کریں',
      healthRecord: 'صحت کا ریکارڈ', allAssessments: 'تمام صحت معائنے', filterLabel: 'فوری توجہ کے مطابق ریکارڈ دیکھیں', filterAll: 'تمام', filterLow: 'کم', filterMedium: 'توجہ درکار', filterHigh: 'فوری',
      someUnavailable: 'کچھ ریکارڈ کی مکمل معلومات نہیں دکھائی جا سکیں۔', noFilterMatches: 'اس انتخاب میں کوئی معائنہ موجود نہیں ہے۔', tryAgain: 'دوبارہ کوشش کریں',
      missingTitle: 'جانور کا ریکارڈ نہیں ملا', missingMessage: 'صحت کی تفصیل دیکھنے کے لیے درست جانور منتخب کریں۔', notFoundTitle: 'جانور کا ریکارڈ نہیں ملا',
      notFoundMessage: 'یہ جانور موجود نہیں یا اس کا ریکارڈ حذف ہو چکا ہے۔', connectionTitle: 'صحت کا ریکارڈ ابھی دستیاب نہیں', connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔',
      malformedTitle: 'صحت کا ریکارڈ مکمل نہیں دکھایا جا سکتا', malformedMessage: 'ریکارڈ کی کچھ معلومات سمجھ نہیں آئیں۔ براہِ کرم دوبارہ کوشش کریں۔', forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ ریکارڈ دیکھنے کی اجازت نہیں ہے۔',
      statusCompleted: 'مکمل', statusPending: 'جاری ہے', statusFailed: 'مکمل نہیں ہوا', statusUnknown: 'حالت درج نہیں', urgencyLow: 'کم فوری توجہ', urgencyMedium: 'توجہ درکار', urgencyHigh: 'فوری توجہ',
      possibleConditions: 'ممکنہ حالتیں', noConditions: 'کوئی ممکنہ حالت درج نہیں', pendingAssessment: 'معائنہ مکمل ہو رہا ہے', failedAssessment: 'معائنہ مکمل نہیں ہو سکا',
      reportedSymptoms: 'بتائی گئی علامات', noSymptoms: 'کوئی علامات درج نہیں', viewResult: 'نتیجہ دیکھیں', dateUnavailable: 'تاریخ درج نہیں',
      selectCompare: 'موازنے کے لیے منتخب کریں', selectedCompare: 'موازنے کے لیے منتخب', compareLimit: 'موازنے کے لیے صرف دو معائنے منتخب کیے جا سکتے ہیں۔', compareReady: 'دو معائنے منتخب ہو گئے', compareReadyHelp: 'دونوں ریکارڈ ساتھ دیکھنے کے لیے آگے بڑھیں۔', compareSelected: 'منتخب معائنوں کا موازنہ کریں',
      footerCare: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔', footerDisclaimer: 'AI کی رائے ابتدائی رہنمائی ہے، ڈاکٹر کا متبادل نہیں۔'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language', logout: 'Logout', backToProfile: 'Back to Animal Profile',
      loadingLabel: 'Loading health history', historyTitle: 'Health History', historySubtitle: 'Review this animal’s previous health assessments in one place.',
      noAssessments: 'No health assessments yet.', emptyHelp: 'Return to the Animal Profile to begin the first assessment.', startAssessment: 'Start Health Assessment',
      healthRecord: 'Health record', allAssessments: 'All Health Assessments', filterLabel: 'Filter records by urgency', filterAll: 'All', filterLow: 'Low', filterMedium: 'Needs attention', filterHigh: 'Urgent',
      someUnavailable: 'Complete information could not be shown for some records.', noFilterMatches: 'No assessments match this selection.', tryAgain: 'Try again',
      missingTitle: 'Animal record not found', missingMessage: 'Select a valid animal to view its health history.', notFoundTitle: 'Animal record not found',
      notFoundMessage: 'This animal does not exist or its record may have been removed.', connectionTitle: 'Health history unavailable right now', connectionMessage: 'We could not connect. Please try again in a little while.',
      malformedTitle: 'Health history cannot be shown completely', malformedMessage: 'Some record information could not be understood. Please try again.', forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to access this record.',
      statusCompleted: 'Completed', statusPending: 'Pending', statusFailed: 'Not completed', statusUnknown: 'Status unavailable', urgencyLow: 'Low urgency', urgencyMedium: 'Needs attention', urgencyHigh: 'Urgent attention',
      possibleConditions: 'Possible conditions', noConditions: 'No possible condition recorded', pendingAssessment: 'Assessment is being completed', failedAssessment: 'Assessment could not be completed',
      reportedSymptoms: 'Reported symptoms', noSymptoms: 'No symptoms recorded', viewResult: 'View Result', dateUnavailable: 'Date not recorded',
      selectCompare: 'Select to compare', selectedCompare: 'Selected for comparison', compareLimit: 'Only two assessments can be selected for comparison.', compareReady: 'Two assessments selected', compareReadyHelp: 'Continue to view both records together.', compareSelected: 'Compare Selected',
      footerCare: 'Built to support better livestock care.', footerDisclaimer: 'AI guidance is preliminary and does not replace a veterinarian.'
    }
  };

  const el = {
    loading: document.querySelector('#history-loading'), error: document.querySelector('#history-error'), page: document.querySelector('#history-page'), empty: document.querySelector('#history-empty'),
    content: document.querySelector('#history-content'), errorTitle: document.querySelector('#history-error-title'), errorMessage: document.querySelector('#history-error-message'), retry: document.querySelector('#retry-history'),
    profileLink: document.querySelector('#profile-link'), errorProfileLink: document.querySelector('#error-profile-link'), startLink: document.querySelector('#start-assessment-link'),
    animalIcon: document.querySelector('#animal-icon'), animalSummary: document.querySelector('#animal-summary'), list: document.querySelector('#history-list'), filterEmpty: document.querySelector('#filter-empty'), malformedNotice: document.querySelector('#malformed-notice'),
    compareTray: document.querySelector('#compare-tray'), compareButton: document.querySelector('#compare-selected')
  };

  let language = window.MaweshiI18n.getLanguage();
  let animal = null;
  let assessments = [];
  let currentFilter = 'all';
  let state = 'loading';
  let errorKind = null;
  let skippedRecords = 0;
  let selectedIds = [];

  function t(key) { return copy[language][key] || key; }

  const api = {
    getAnimal: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, { headers: { Accept: 'application/json' } }),
    getAssessments: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/assessments`, { headers: { Accept: 'application/json' } })
  };

  function setProfileLinks() {
    const destination = animalId && animalId.trim() ? `animal-profile.html?id=${encodeURIComponent(animalId)}` : 'index.html';
    [el.profileLink, el.errorProfileLink, el.startLink].forEach((link) => { link.href = destination; });
  }

  function animalIcon(type) {
    const value = type === null || type === undefined ? '' : String(type).toLowerCase();
    if (value.includes('buffalo') || value.includes('بھینس')) return '🐃';
    if (value.includes('goat') || value.includes('بکری') || value.includes('بکرا')) return '🐐';
    if (value.includes('sheep') || value.includes('بھیڑ') || value.includes('دنب')) return '🐑';
    if (value.includes('cow') || value.includes('cattle') || value.includes('گائے') || value.includes('بیل')) return '🐄';
    return '🐾';
  }

  function safeTime(raw) {
    const value = new Date(raw || 0).getTime();
    return Number.isNaN(value) ? 0 : value;
  }

  function formatDate(raw) {
    const date = new Date(raw || 0);
    if (!raw || Number.isNaN(date.getTime())) return t('dateUnavailable');
    return new Intl.DateTimeFormat(language === 'ur' ? 'ur-PK' : 'en-PK', { dateStyle: 'medium', timeStyle: 'short' }).format(date);
  }

  function validRecord(record) {
    return record && typeof record === 'object' && record.id !== null && record.id !== undefined && String(record.id).trim() !== '';
  }

  function normalizedStatus(record) {
    return ['completed', 'pending', 'failed'].includes(record.status) ? record.status : 'unknown';
  }

  function recordUrgency(record) {
    if (normalizedStatus(record) !== 'completed') return null;
    const result = record.diagnosis_result;
    return result && typeof result === 'object' && ['low', 'medium', 'high'].includes(result.urgency_level) ? result.urgency_level : null;
  }

  function statusLabel(status) {
    return t(status === 'completed' ? 'statusCompleted' : status === 'pending' ? 'statusPending' : status === 'failed' ? 'statusFailed' : 'statusUnknown');
  }

  function urgencyLabel(urgency) {
    return t(urgency === 'low' ? 'urgencyLow' : urgency === 'high' ? 'urgencyHigh' : 'urgencyMedium');
  }

  function conditionSummary(record, status) {
    if (status === 'pending') return t('pendingAssessment');
    if (status === 'failed') return t('failedAssessment');
    const result = record.diagnosis_result;
    const conditions = result && typeof result === 'object' && Array.isArray(result.possible_conditions)
      ? result.possible_conditions.filter((condition) => typeof condition === 'string' && condition.trim())
      : [];
    return conditions.length ? conditions.join(' · ') : t('noConditions');
  }

  function createChip(text, modifier, icon) {
    const chip = document.createElement('span');
    chip.className = `history-chip history-chip--${modifier}`;
    chip.textContent = `${icon} ${text}`;
    return chip;
  }

  function createEntry(record) {
    const status = normalizedStatus(record);
    const urgency = recordUrgency(record);
    const entry = document.createElement('article');
    entry.className = `history-entry history-entry--${status === 'failed' || status === 'pending' || status === 'unknown' ? status : urgency || 'unknown'}`;

    const top = document.createElement('div'); top.className = 'entry-top';
    const date = document.createElement('time'); date.dateTime = record.created_at || ''; date.textContent = formatDate(record.created_at);
    const badges = document.createElement('div'); badges.className = 'entry-badges';
    badges.appendChild(createChip(statusLabel(status), status, status === 'completed' ? '✓' : status === 'pending' ? '…' : status === 'failed' ? '!' : '–'));
    if (urgency) badges.appendChild(createChip(urgencyLabel(urgency), urgency, urgency === 'low' ? '✓' : '!'));
    top.append(date, badges);

    const heading = document.createElement('h3'); heading.textContent = conditionSummary(record, status); heading.dir = 'auto';
    const symptomsLabel = document.createElement('p'); symptomsLabel.className = 'entry-symptoms-label'; symptomsLabel.textContent = t('reportedSymptoms');
    const symptoms = document.createElement('p'); symptoms.className = 'entry-symptoms'; symptoms.textContent = typeof record.symptoms === 'string' && record.symptoms.trim() ? record.symptoms : t('noSymptoms'); symptoms.dir = 'auto';
    const recordId = String(record.id);
    const selected = selectedIds.includes(recordId);
    const selectionFull = selectedIds.length >= 2;
    entry.classList.toggle('is-selected', selected);

    const actions = document.createElement('div'); actions.className = 'entry-actions';
    const resultLink = document.createElement('a'); resultLink.className = 'entry-result-link'; resultLink.href = `assessment-result.html?id=${encodeURIComponent(record.id)}`; resultLink.textContent = t('viewResult');
    const compareButton = document.createElement('button');
    compareButton.type = 'button';
    compareButton.className = 'entry-compare-button';
    compareButton.dataset.compareId = recordId;
    compareButton.setAttribute('aria-pressed', String(selected));
    compareButton.disabled = selectionFull && !selected;
    if (compareButton.disabled) compareButton.title = t('compareLimit');
    compareButton.innerHTML = `<span class="compare-check" aria-hidden="true">${selected ? '✓' : ''}</span><span>${t(selected ? 'selectedCompare' : 'selectCompare')}</span>`;
    actions.append(resultLink, compareButton);
    entry.append(top, heading, symptomsLabel, symptoms, actions);
    return entry;
  }

  function renderCompareTray() {
    const ready = selectedIds.length === 2 && selectedIds.every((id) => assessments.some((record) => String(record.id) === id));
    el.compareTray.classList.toggle('hidden', !ready);
    el.compareButton.disabled = !ready;
  }

  function toggleComparison(recordId) {
    if (!assessments.some((record) => String(record.id) === recordId)) return;
    if (selectedIds.includes(recordId)) selectedIds = selectedIds.filter((id) => id !== recordId);
    else if (selectedIds.length < 2) selectedIds = [...selectedIds, recordId];
    renderHistory();
  }

  function compareSelected() {
    const selectedRecords = selectedIds
      .map((id) => assessments.find((record) => String(record.id) === id))
      .filter(Boolean)
      .sort((a, b) => safeTime(a.created_at) - safeTime(b.created_at));
    if (selectedRecords.length !== 2 || !animalId) return;
    const query = new URLSearchParams({ id: animalId, assessment1: String(selectedRecords[0].id), assessment2: String(selectedRecords[1].id) });
    window.location.assign(`assessment-compare.html?${query.toString()}`);
  }

  function renderHeader() {
    if (!animal) return;
    el.animalIcon.textContent = animalIcon(animal.animal_type);
    el.animalSummary.textContent = [animal.name, animal.animal_type].filter((item) => item !== null && item !== undefined && String(item).trim()).join(' · ');
    document.title = `${t('historyTitle')} · ${animal.name || ''} | Maweshi Muhafiz`;
  }

  function renderHistory() {
    if (state === 'loading') return;
    if (state !== 'content') el.compareTray.classList.add('hidden');
    el.loading.classList.add('hidden');
    el.error.classList.toggle('hidden', state !== 'error');
    el.page.classList.toggle('hidden', state === 'error');
    if (state === 'error') {
      el.errorTitle.textContent = t(`${errorKind}Title`);
      el.errorMessage.textContent = t(`${errorKind}Message`);
      el.retry.classList.toggle('hidden', errorKind === 'missing' || errorKind === 'notFound');
      return;
    }

    renderHeader();
    el.empty.classList.toggle('hidden', state !== 'empty');
    el.content.classList.toggle('hidden', state !== 'content');
    if (state !== 'content') return;

    document.querySelectorAll('[data-history-filter]').forEach((button) => {
      const selected = button.dataset.historyFilter === currentFilter;
      button.classList.toggle('is-active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });

    const visible = currentFilter === 'all' ? assessments : assessments.filter((record) => recordUrgency(record) === currentFilter);
    const fragment = document.createDocumentFragment();
    visible.forEach((record) => fragment.appendChild(createEntry(record)));
    el.list.replaceChildren(fragment);
    el.list.classList.toggle('hidden', visible.length === 0);
    el.filterEmpty.classList.toggle('hidden', visible.length !== 0);
    el.malformedNotice.classList.toggle('hidden', skippedRecords === 0);
    renderCompareTray();
  }

  async function loadHistory() {
    if (!animalId || !animalId.trim()) {
      state = 'error'; errorKind = 'missing'; renderHistory(); return;
    }
    state = 'loading'; errorKind = null;
    el.error.classList.add('hidden'); el.page.classList.add('hidden'); el.loading.classList.remove('hidden');
    try {
      animal = await api.getAnimal(animalId);
      const data = await api.getAssessments(animalId);
      if (!Array.isArray(data)) { state = 'error'; errorKind = 'malformed'; renderHistory(); return; }
      skippedRecords = data.filter((record) => !validRecord(record)).length;
      assessments = data.filter(validRecord).sort((a, b) => safeTime(b.created_at) - safeTime(a.created_at));
      selectedIds = selectedIds.filter((id) => assessments.some((record) => String(record.id) === id));
      if (data.length > 0 && assessments.length === 0) { state = 'error'; errorKind = 'malformed'; }
      else state = assessments.length ? 'content' : 'empty';
      renderHistory();
    } catch (error) {
      console.error('Health history could not be loaded.', error);
      state = 'error'; errorKind = error.status === 404 ? 'notFound' : error.status === 403 ? 'forbidden' : 'connection'; renderHistory();
    }
  }

  function applyLanguage(nextLanguage) {
    language = window.MaweshiI18n.applyPage(nextLanguage, copy).language;
    renderHistory();
  }

  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) applyLanguage(languageButton.dataset.language);
    const filterButton = event.target.closest('[data-history-filter]');
    if (filterButton) { currentFilter = filterButton.dataset.historyFilter; renderHistory(); }
    const compareControl = event.target.closest('[data-compare-id]');
    if (compareControl && !compareControl.disabled) toggleComparison(compareControl.dataset.compareId);
  });
  el.retry.addEventListener('click', loadHistory);
  el.compareButton.addEventListener('click', compareSelected);

  setProfileLinks();
  applyLanguage(language);
  loadHistory();
})();
