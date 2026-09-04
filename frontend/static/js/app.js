(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const ANIMALS_ENDPOINT = `${API_BASE}/api/animals`;
  const AREA_INSIGHTS_ENDPOINT = `${API_BASE}/api/insights/area`;

  const translations = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں',
      checkingConnection: 'رابطہ دیکھا جا رہا ہے', connected: 'رابطہ قائم ہے', unavailable: 'رابطہ دستیاب نہیں',
      addAnimal: 'جانور شامل کریں', addShort: 'شامل کریں', animalRecords: 'جانوروں کا ریکارڈ',
      pageHeading: 'اپنے مویشیوں کا ریکارڈ آسانی سے سنبھالیں', pageIntro: 'ہر جانور کی ضروری معلومات ایک جگہ رکھیں تاکہ وقت پر بہتر دیکھ بھال ہو سکے۔',
      summaryLabel: 'مویشیوں کا خلاصہ', totalAnimals: 'کل جانور', healthyAnimals: 'صحت مند جانور', attentionAnimals: 'توجہ طلب جانور',
      allAnimals: 'تمام جانور', recordsSaved: 'مویشی محافظ میں محفوظ ریکارڈ', refresh: 'تازہ کریں',
      refreshLabel: 'جانوروں کا ریکارڈ دوبارہ دیکھیں', loadingLabel: 'جانوروں کا ریکارڈ لوڈ ہو رہا ہے',
      footerCare: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔', footerDisclaimer: 'AI کی رائے ابتدائی رہنمائی ہے، ڈاکٹر کا متبادل نہیں۔',
      newRecord: 'نیا ریکارڈ', addAnAnimal: 'جانور شامل کریں', closeFormLabel: 'فارم بند کریں',
      formIntro: 'ضروری معلومات درج کریں۔ باقی خانے خالی چھوڑ سکتے ہیں۔', name: 'نام', namePlaceholder: 'مثلاً رانی',
      animalType: 'جانور کی قسم', typePlaceholder: 'مثلاً گائے', breed: 'نسل', breedPlaceholder: 'مثلاً ساہیوال',
      gender: 'جنس', selectGender: 'جنس منتخب کریں', female: 'مادہ', male: 'نر', ageYears: 'عمر (سال)', agePlaceholder: 'مثلاً 3',
      weightKg: 'وزن (کلو)', weightPlaceholder: 'مثلاً 320', color: 'رنگ', colorPlaceholder: 'مثلاً بھورا', region: 'علاقہ', regionPlaceholder: 'مثلاً لاہور', currentHealth: 'موجودہ صحت', notRecorded: 'درج نہیں',
      healthy: 'صحت مند', needsAttention: 'توجہ درکار', underTreatment: 'علاج جاری ہے', notes: 'اضافی باتیں',
      notesPlaceholder: 'پہچان کی علامت یا دیکھ بھال کی اہم بات', cancel: 'منسوخ کریں', saveAnimal: 'جانور محفوظ کریں', saving: 'محفوظ ہو رہا ہے…',
      emptyTitle: 'ابھی کوئی جانور شامل نہیں کیا گیا', emptyMessage: 'اپنا پہلا جانور شامل کریں اور اس کا ریکارڈ سنبھالنا شروع کریں۔',
      addFirstAnimal: 'اپنا پہلا جانور شامل کریں', errorTitle: 'ریکارڈ ابھی دستیاب نہیں',
      errorMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔', forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ ریکارڈ دیکھنے کی اجازت نہیں ہے۔', tryAgain: 'دوبارہ کوشش کریں',
      unreadableResponse: 'جواب سمجھ نہیں آیا۔ دوبارہ کوشش کریں۔', requestFailed: 'کام مکمل نہیں ہو سکا۔ دوبارہ کوشش کریں۔',
      updated: 'تازہ کیا گیا', typeNotRecorded: 'قسم درج نہیں', age: 'عمر', weight: 'وزن',
      yearUnit: 'سال', kgUnit: 'کلو', noNotes: 'کوئی اضافی بات درج نہیں۔', viewProfile: 'پروفائل دیکھیں', closeProfile: 'پروفائل بند کریں', logout: 'لاگ آؤٹ',
      areaInsightsKicker: 'آپ کے جانوروں کا ریکارڈ', areaInsightsTitle: 'علاقے کے حساب سے صحت کی معلومات', areaInsightsSubtitle: 'آپ کے جانوروں کے صحت معائنے ان کے درج کیے گئے علاقے کے مطابق۔', areaInsightsLoading: 'علاقے کی صحت کی معلومات دیکھی جا رہی ہیں',
      areaInsightsUnavailable: 'علاقے کی معلومات ابھی دستیاب نہیں ہیں۔', areaInsightsErrorHelp: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔', areaInsightsMalformed: 'علاقے کی معلومات دکھائی نہیں جا سکیں۔', areaInsightsMalformedHelp: 'ریکارڈ کی کچھ معلومات سمجھ نہیں آئیں۔ براہِ کرم دوبارہ کوشش کریں۔',
      areaInsightsEmpty: 'ابھی علاقے کے حساب سے کوئی صحت ریکارڈ موجود نہیں ہے۔', areaInsightsEmptyHelp: 'صحت کا معائنہ محفوظ ہونے کے بعد اس کی گنتی یہاں نظر آئے گی۔', areaInsightsScope: 'یہ گنتی صرف آپ کے اکاؤنٹ میں موجود جانوروں کے معائنوں کی ہے، پورے علاقے یا دوسرے کسانوں کی نہیں۔', regionNotRecorded: 'علاقہ درج نہیں', totalHealthAssessments: 'کل صحت معائنے', urgentFlaggedAssessments: 'فوری توجہ والے معائنے'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language',
      checkingConnection: 'Checking connection', connected: 'Connected', unavailable: 'Connection unavailable',
      addAnimal: 'Add animal', addShort: 'Add', animalRecords: 'Animal records', pageHeading: 'Your livestock, clearly organised',
      pageIntro: 'Keep essential details in one place so every animal can receive timely, informed care.',
      summaryLabel: 'Livestock summary', totalAnimals: 'Total animals', healthyAnimals: 'Healthy animals', attentionAnimals: 'Animals needing attention',
      allAnimals: 'All animals', recordsSaved: 'Records saved in Maweshi Muhafiz', refresh: 'Refresh', refreshLabel: 'Refresh animal records',
      loadingLabel: 'Loading animal records', footerCare: 'Built to support better livestock care.',
      footerDisclaimer: 'AI guidance is preliminary and does not replace a veterinarian.', newRecord: 'New record', addAnAnimal: 'Add an animal',
      closeFormLabel: 'Close add animal form', formIntro: 'Start with the essential details. You can leave optional information blank.',
      name: 'Name', namePlaceholder: 'e.g. Rani', animalType: 'Animal type', typePlaceholder: 'e.g. Cow', breed: 'Breed',
      breedPlaceholder: 'e.g. Sahiwal', gender: 'Gender', selectGender: 'Select gender', female: 'Female', male: 'Male',
      ageYears: 'Age in years', agePlaceholder: 'e.g. 3', weightKg: 'Weight in kg', weightPlaceholder: 'e.g. 320', color: 'Color', colorPlaceholder: 'e.g. Brown', region: 'Region', regionPlaceholder: 'e.g. Lahore',
      currentHealth: 'Current health status', notRecorded: 'Not recorded', healthy: 'Healthy', needsAttention: 'Needs attention',
      underTreatment: 'Under treatment', notes: 'Notes', notesPlaceholder: 'Identification marks or useful care notes', cancel: 'Cancel',
      saveAnimal: 'Save animal', saving: 'Saving…', emptyTitle: 'No animals added yet',
      emptyMessage: 'Add your first animal to begin keeping its care information in one place.', addFirstAnimal: 'Add your first animal',
      errorTitle: 'Records are unavailable right now', errorMessage: 'We could not connect. Please try again in a little while.', forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to access this record.', tryAgain: 'Try again',
      unreadableResponse: 'We could not understand the response. Please try again.', requestFailed: 'The request could not be completed.',
      updated: 'Updated', typeNotRecorded: 'Type not recorded', age: 'Age', weight: 'Weight', yearUnit: 'yr', kgUnit: 'kg',
      noNotes: 'No additional notes recorded.', viewProfile: 'View Profile', closeProfile: 'Close Profile', logout: 'Logout',
      areaInsightsKicker: 'Your animals’ records', areaInsightsTitle: 'Health insights by recorded area', areaInsightsSubtitle: 'Health assessments for your animals, grouped by the area saved on their records.', areaInsightsLoading: 'Loading area health insights',
      areaInsightsUnavailable: 'Area insights are unavailable right now.', areaInsightsErrorHelp: 'We could not connect. Please try again in a little while.', areaInsightsMalformed: 'Area insights could not be displayed.', areaInsightsMalformedHelp: 'Some record information could not be understood. Please try again.',
      areaInsightsEmpty: 'No area-based health activity yet.', areaInsightsEmptyHelp: 'Assessment counts will appear here after a health assessment is saved.', areaInsightsScope: 'These counts only use assessments for animals in your account. They are not statistics for the wider area or other farmers.', regionNotRecorded: 'Region not recorded', totalHealthAssessments: 'Total assessments', urgentFlaggedAssessments: 'Urgent or flagged'
    }
  };

  const elements = {
    state: document.querySelector('#animal-state'), grid: document.querySelector('#animal-grid'), template: document.querySelector('#animal-card-template'),
    totalCount: document.querySelector('#total-count'), healthyCount: document.querySelector('#healthy-count'), attentionCount: document.querySelector('#attention-count'),
    updated: document.querySelector('#last-updated'), indicator: document.querySelector('#api-indicator'), refreshButton: document.querySelector('#refresh-button'),
    dialog: document.querySelector('#animal-dialog'), form: document.querySelector('#animal-form'), formAlert: document.querySelector('#form-alert'),
    saveButton: document.querySelector('#save-animal-button'),
    insightsLoading: document.querySelector('#area-insights-loading'), insightsContent: document.querySelector('#area-insights-content'), insightsList: document.querySelector('#area-insights-list'),
    insightsEmpty: document.querySelector('#area-insights-empty'), insightsError: document.querySelector('#area-insights-error'), insightsErrorTitle: document.querySelector('#area-insights-error-title'), insightsErrorMessage: document.querySelector('#area-insights-error-message'), insightsRetry: document.querySelector('#retry-area-insights')
  };

  let currentLanguage = window.MaweshiI18n.getLanguage();
  let currentAnimals = null;
  let currentState = null;
  let connectionState = 'checking';
  let areaInsights = [];
  let areaInsightsState = 'loading';

  function t(key) { return translations[currentLanguage][key] || key; }
  function text(value, fallback = t('notRecorded')) {
    return value === null || value === undefined || String(value).trim() === '' ? fallback : String(value);
  }
  function normaliseStatus(value) { return text(value, '').trim().toLowerCase(); }
  function isHealthy(value) { return ['healthy', 'good', 'fit'].includes(normaliseStatus(value)); }
  function needsAttention(value) {
    const status = normaliseStatus(value);
    return status.includes('attention') || status.includes('treatment') || status.includes('sick') || status.includes('critical');
  }
  function translateValue(value) {
    return { Female: t('female'), Male: t('male'), Healthy: t('healthy'), 'Needs attention': t('needsAttention'), 'Under treatment': t('underTreatment') }[value] || value;
  }

  function translatePage() {
    currentLanguage = window.MaweshiI18n.applyPage(currentLanguage, translations).language;
    updateConnection(connectionState);
    renderAreaInsights();
  }

  function setLanguage(language) {
    if (!translations[language] || language === currentLanguage) return;
    currentLanguage = language;
    window.MaweshiI18n.setLanguage(language);
    translatePage();
    if (currentAnimals) renderAnimals(currentAnimals);
    else if (currentState) showState(currentState);
  }

  function updateConnection(state) {
    connectionState = state;
    const dot = elements.indicator.querySelector('.status-dot');
    const label = elements.indicator.querySelector('span:last-child');
    dot.className = `status-dot status-dot--${state === 'online' ? 'online' : state === 'offline' ? 'offline' : 'checking'}`;
    label.textContent = t(state === 'online' ? 'connected' : state === 'offline' ? 'unavailable' : 'checkingConnection');
  }

  function setSummary(animals) {
    elements.totalCount.textContent = animals.length;
    elements.healthyCount.textContent = animals.filter((animal) => isHealthy(animal.health_status)).length;
    elements.attentionCount.textContent = animals.filter((animal) => needsAttention(animal.health_status)).length;
  }

  function validInsight(entry) {
    return entry && typeof entry === 'object'
      && typeof entry.region === 'string' && entry.region.trim()
      && Number.isInteger(entry.total_assessments) && entry.total_assessments >= 0
      && Number.isInteger(entry.flagged_cases) && entry.flagged_cases >= 0
      && entry.flagged_cases <= entry.total_assessments;
  }

  function createInsightRow(entry) {
    const row = document.createElement('article');
    row.className = 'area-insight-row';

    const region = document.createElement('h3');
    region.className = 'area-insight-region';
    region.textContent = entry.region.trim().toLowerCase() === 'unknown' ? t('regionNotRecorded') : entry.region;
    region.dir = entry.region.trim().toLowerCase() === 'unknown' ? '' : 'auto';

    const total = document.createElement('div');
    total.className = 'area-insight-metric';
    const totalValue = document.createElement('strong'); totalValue.textContent = String(entry.total_assessments);
    const totalLabel = document.createElement('span'); totalLabel.textContent = t('totalHealthAssessments');
    total.append(totalValue, totalLabel);

    const flagged = document.createElement('div');
    flagged.className = 'area-insight-metric area-insight-metric--flagged';
    const flaggedValue = document.createElement('strong'); flaggedValue.textContent = String(entry.flagged_cases);
    const flaggedLabel = document.createElement('span'); flaggedLabel.textContent = t('urgentFlaggedAssessments');
    flagged.append(flaggedValue, flaggedLabel);

    row.append(region, total, flagged);
    return row;
  }

  function renderAreaInsights() {
    elements.insightsLoading.classList.toggle('hidden', areaInsightsState !== 'loading');
    elements.insightsContent.classList.toggle('hidden', areaInsightsState !== 'content');
    elements.insightsEmpty.classList.toggle('hidden', areaInsightsState !== 'empty');
    elements.insightsError.classList.toggle('hidden', !['error', 'malformed'].includes(areaInsightsState));
    elements.insightsRetry.classList.toggle('hidden', !['error', 'malformed'].includes(areaInsightsState));

    if (['error', 'malformed'].includes(areaInsightsState)) {
      const malformed = areaInsightsState === 'malformed';
      elements.insightsErrorTitle.textContent = t(malformed ? 'areaInsightsMalformed' : 'areaInsightsUnavailable');
      elements.insightsErrorMessage.textContent = t(malformed ? 'areaInsightsMalformedHelp' : 'areaInsightsErrorHelp');
    }
    if (areaInsightsState === 'content') {
      const fragment = document.createDocumentFragment();
      areaInsights.forEach((entry) => fragment.appendChild(createInsightRow(entry)));
      elements.insightsList.replaceChildren(fragment);
    }
  }

  async function loadAreaInsights() {
    areaInsightsState = 'loading';
    renderAreaInsights();
    try {
      const data = await window.MaweshiAuth.request(AREA_INSIGHTS_ENDPOINT, { headers: { Accept: 'application/json' } });
      if (!Array.isArray(data) || !data.every(validInsight)) {
        areaInsights = [];
        areaInsightsState = 'malformed';
      } else {
        areaInsights = data;
        areaInsightsState = data.length ? 'content' : 'empty';
      }
    } catch (error) {
      console.error('Area insights could not be loaded.', error);
      areaInsights = [];
      areaInsightsState = 'error';
    }
    renderAreaInsights();
  }

  function showState(kind) {
    currentState = kind;
    const isEmpty = kind === 'empty';
    const isForbidden = kind === 'forbidden';
    const icon = isEmpty
      ? '<path d="M5 10.5V18m14-7.5V18M7 16h10M7 9.5c1.5-2 3.1-3 5-3s3.5 1 5 3v4.7H7V9.5ZM7 10 4 7m13 3 3-3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
      : '<path d="M12 8v5m0 3h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/>';
    elements.state.innerHTML = `<div class="state-panel state-panel--${kind}">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">${icon}</svg>
      <h3>${t(isEmpty ? 'emptyTitle' : isForbidden ? 'forbiddenTitle' : 'errorTitle')}</h3><p>${t(isEmpty ? 'emptyMessage' : isForbidden ? 'forbiddenMessage' : 'errorMessage')}</p>
      <button type="button" class="btn ${isEmpty ? 'btn-primary' : 'btn-secondary'} mt-5" ${isEmpty ? 'data-open-animal-dialog' : 'data-retry'}>${t(isEmpty ? 'addFirstAnimal' : 'tryAgain')}</button>
    </div>`;
    elements.state.classList.remove('hidden');
    elements.state.setAttribute('aria-busy', 'false');
    elements.grid.classList.add('hidden');
  }

  function renderAnimal(animal) {
    const card = elements.template.content.cloneNode(true);
    const status = text(animal.health_status);
    const badge = card.querySelector('.health-badge');
    badge.textContent = translateValue(status);
    badge.classList.add(isHealthy(status) ? 'health-badge--healthy' : needsAttention(status) ? 'health-badge--attention' : 'health-badge--unknown');
    card.querySelector('.animal-name').textContent = text(animal.name);
    card.querySelector('.animal-kind').textContent = [text(animal.animal_type, ''), text(animal.breed, '')].filter(Boolean).join(' · ') || t('typeNotRecorded');
    card.querySelector('[data-field="age"]').textContent = animal.age !== null && animal.age !== undefined ? `${animal.age} ${t('yearUnit')}` : '—';
    card.querySelector('[data-field="weight"]').textContent = animal.weight !== null && animal.weight !== undefined ? `${animal.weight} ${t('kgUnit')}` : '—';
    card.querySelector('[data-field="gender"]').textContent = translateValue(text(animal.gender, '—'));
    card.querySelector('.animal-notes').textContent = text(animal.notes, t('noNotes'));
    card.querySelectorAll('[data-card-i18n]').forEach((node) => { node.textContent = t(node.dataset.cardI18n); });
    card.querySelector('[data-view-profile]').dataset.animalId = animal.id;
    return card;
  }

  function renderAnimals(animals) {
    currentAnimals = animals;
    elements.grid.replaceChildren();
    setSummary(animals);
    if (animals.length === 0) { showState('empty'); return; }
    currentState = null;
    const fragment = document.createDocumentFragment();
    animals.forEach((animal) => fragment.appendChild(renderAnimal(animal)));
    elements.grid.appendChild(fragment);
    elements.state.classList.add('hidden');
    elements.grid.classList.remove('hidden');
  }

  async function loadAnimals() {
    elements.refreshButton.disabled = true;
    elements.state.setAttribute('aria-busy', 'true');
    try {
      const data = await window.MaweshiAuth.request(ANIMALS_ENDPOINT, { headers: { Accept: 'application/json' } });
      renderAnimals(Array.isArray(data) ? data : []);
      updateConnection('online');
      const locale = currentLanguage === 'ur' ? 'ur-PK' : 'en-PK';
      elements.updated.textContent = `${t('updated')} ${new Intl.DateTimeFormat(locale, { hour: 'numeric', minute: '2-digit' }).format(new Date())}`;
    } catch (error) {
      currentAnimals = null;
      setSummary([]);
      showState(error.status === 403 ? 'forbidden' : 'error');
      updateConnection(error.status === 403 ? 'online' : 'offline');
      elements.updated.textContent = '';
      console.error(error);
    } finally {
      elements.refreshButton.disabled = false;
      elements.state.setAttribute('aria-busy', 'false');
    }
  }

  function openDialog() {
    elements.formAlert.classList.add('hidden');
    elements.formAlert.textContent = '';
    elements.dialog.showModal();
    requestAnimationFrame(() => document.querySelector('#animal-name').focus());
  }
  function closeDialog() { if (!elements.saveButton.disabled) elements.dialog.close(); }
  function optionalString(formData, field) {
    const value = String(formData.get(field) || '').trim();
    return value || null;
  }
  function buildAnimalPayload(formData) {
    const payload = { name: String(formData.get('name') || '').trim(), animal_type: String(formData.get('animal_type') || '').trim() };
    ['breed', 'gender', 'color', 'health_status', 'region', 'notes'].forEach((field) => {
      const value = optionalString(formData, field);
      if (value !== null) payload[field] = value;
    });
    ['age', 'weight'].forEach((field) => {
      const raw = String(formData.get(field) || '').trim();
      if (raw !== '') payload[field] = Number(raw);
    });
    return payload;
  }

  async function saveAnimal(event) {
    event.preventDefault();
    elements.formAlert.classList.add('hidden');
    if (!elements.form.reportValidity()) return;
    elements.saveButton.disabled = true;
    elements.saveButton.textContent = t('saving');
    try {
      await window.MaweshiAuth.request(ANIMALS_ENDPOINT, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(buildAnimalPayload(new FormData(elements.form)))
      });
      elements.form.reset();
      elements.dialog.close();
      await loadAnimals();
    } catch (error) {
      elements.formAlert.textContent = currentLanguage === 'ur' ? t('requestFailed') : error.message;
      elements.formAlert.classList.remove('hidden');
    } finally {
      elements.saveButton.disabled = false;
      elements.saveButton.textContent = t('saveAnimal');
    }
  }

  function openProfile(button) {
    const animalId = button.dataset.animalId;
    if (animalId !== undefined && animalId !== null && animalId !== '') {
      window.location.href = `animal-profile.html?id=${encodeURIComponent(animalId)}`;
    }
  }

  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    const profileButton = event.target.closest('[data-view-profile]');
    if (languageButton) setLanguage(languageButton.dataset.language);
    if (profileButton) openProfile(profileButton);
    if (event.target.closest('[data-open-animal-dialog]')) openDialog();
    if (event.target.closest('[data-close-animal-dialog]')) closeDialog();
    if (event.target.closest('[data-retry]')) loadAnimals();
  });
  elements.dialog.addEventListener('click', (event) => { if (event.target === elements.dialog) closeDialog(); });
  elements.dialog.addEventListener('cancel', (event) => { if (elements.saveButton.disabled) event.preventDefault(); });
  elements.refreshButton.addEventListener('click', () => { loadAnimals(); loadAreaInsights(); });
  elements.insightsRetry.addEventListener('click', loadAreaInsights);
  elements.form.addEventListener('submit', saveAnimal);

  translatePage();
  loadAnimals();
  loadAreaInsights();
})();
