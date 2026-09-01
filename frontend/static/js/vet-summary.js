(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const params = new URLSearchParams(window.location.search);
  const animalId = params.get('animal_id');
  const assessmentId = params.get('assessment_id');

  const copy = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں', logout: 'لاگ آؤٹ',
      backToResult: 'معائنے کے نتیجے پر واپس جائیں', printSummary: 'خلاصہ پرنٹ کریں', loadingLabel: 'ڈاکٹر کے لیے خلاصہ تیار ہو رہا ہے', tryAgain: 'دوبارہ کوشش کریں',
      missingTitle: 'خلاصے کی معلومات مکمل نہیں', missingMessage: 'ڈاکٹر کے لیے خلاصہ دیکھنے کو درست جانور اور معائنہ منتخب کریں۔',
      notFoundTitle: 'خلاصہ دستیاب نہیں', notFoundMessage: 'یہ جانور یا معائنہ موجود نہیں یا دستیاب نہیں رہا۔',
      forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ ریکارڈ دیکھنے کی اجازت نہیں ہے۔',
      connectionTitle: 'خلاصہ ابھی دستیاب نہیں', connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔',
      malformedTitle: 'خلاصہ مکمل نہیں دکھایا جا سکتا', malformedMessage: 'محفوظ معلومات کی شکل سمجھ نہیں آئی۔ براہِ کرم دوبارہ کوشش کریں۔',
      documentLabel: 'جانوروں کی صحت کا منظم ریکارڈ', clinicalRecord: 'ڈاکٹر کے لیے ریکارڈ', pageTitle: 'ڈاکٹر کے لیے صحت کا خلاصہ', pageSubtitle: 'جانور کی معلومات اور صحت کے ایک معائنے کا محفوظ خلاصہ',
      summaryReference: 'خلاصہ نمبر', createdDate: 'بننے کی تاریخ', assessmentStatus: 'معائنے کی حالت', redFlagLabel: 'ہنگامی علامت', redFlagTitle: 'فوری توجہ درکار ہے',
      animalRecord: 'جانور کا ریکارڈ', animalInformation: 'جانور کی معلومات', animalName: 'نام', animalType: 'جانور کی قسم', breed: 'نسل', gender: 'جنس', age: 'عمر', weight: 'وزن', color: 'رنگ', healthStatus: 'موجودہ صحت',
      farmerReport: 'کسان کی دی ہوئی معلومات', assessmentInformation: 'معائنے کی معلومات', urgency: 'فوری توجہ', reportedSymptoms: 'بتائی گئی علامات',
      assessmentFindings: 'معائنے کی معلومات', possibleFindings: 'ممکنہ حالتیں اور وضاحت', possibleConditions: 'ممکنہ حالتیں', explanation: 'وضاحت', confidenceNote: 'غیر یقینی بات', noConditions: 'کوئی ممکنہ حالت درج نہیں ہے۔',
      findingsUnavailable: 'معائنے کی مکمل معلومات موجود نہیں ہیں', findingsUnavailableHelp: 'اس خلاصے میں محفوظ تشخیصی معلومات دستیاب نہیں ہیں۔',
      safetyMessage: 'یہ AI کی مدد سے تیار شدہ ابتدائی صحت ریکارڈ ہے اور مستند جانوروں کے ڈاکٹر کی تشخیص کا متبادل نہیں۔', animalId: 'جانور نمبر', assessmentId: 'معائنہ نمبر',
      notRecorded: 'درج نہیں', years: 'سال', kg: 'کلو', statusCompleted: 'مکمل', statusPending: 'جاری ہے', statusFailed: 'مکمل نہیں ہوا', statusUnknown: 'درج نہیں', urgencyLow: 'کم فوری توجہ', urgencyMedium: 'توجہ درکار', urgencyHigh: 'فوری توجہ', urgencyUnknown: 'درج نہیں', noSymptoms: 'کوئی علامات درج نہیں ہیں۔'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language', logout: 'Logout',
      backToResult: 'Back to Assessment Result', printSummary: 'Print Summary', loadingLabel: 'Preparing vet-ready summary', tryAgain: 'Try again',
      missingTitle: 'Summary information is incomplete', missingMessage: 'Select a valid animal and assessment to view the vet-ready summary.',
      notFoundTitle: 'Summary unavailable', notFoundMessage: 'This animal or assessment does not exist or is no longer available.',
      forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to access this record.',
      connectionTitle: 'Summary unavailable right now', connectionMessage: 'We could not connect. Please try again in a little while.',
      malformedTitle: 'Summary cannot be shown completely', malformedMessage: 'Some saved information could not be understood. Please try again.',
      documentLabel: 'Organised livestock health record', clinicalRecord: 'Veterinary record', pageTitle: 'Vet-Ready Case Summary', pageSubtitle: 'A saved snapshot of the animal and one health assessment',
      summaryReference: 'Summary reference', createdDate: 'Created', assessmentStatus: 'Assessment status', redFlagLabel: 'Emergency warning', redFlagTitle: 'Urgent attention required',
      animalRecord: 'Animal record', animalInformation: 'Animal Information', animalName: 'Name', animalType: 'Animal type', breed: 'Breed', gender: 'Gender', age: 'Age', weight: 'Weight', color: 'Color', healthStatus: 'Current health status',
      farmerReport: 'Farmer report', assessmentInformation: 'Assessment Information', urgency: 'Urgency', reportedSymptoms: 'Reported Symptoms',
      assessmentFindings: 'Assessment findings', possibleFindings: 'Possible Conditions and Explanation', possibleConditions: 'Possible conditions', explanation: 'Explanation', confidenceNote: 'Confidence and uncertainty', noConditions: 'No possible condition was recorded.',
      findingsUnavailable: 'Complete assessment findings are unavailable', findingsUnavailableHelp: 'No structured diagnosis result is stored in this summary.',
      safetyMessage: 'This is an AI-assisted preliminary health record and does not replace diagnosis by a qualified veterinarian.', animalId: 'Animal ID', assessmentId: 'Assessment ID',
      notRecorded: 'Not recorded', years: 'years', kg: 'kg', statusCompleted: 'Completed', statusPending: 'Pending', statusFailed: 'Not completed', statusUnknown: 'Not recorded', urgencyLow: 'Low urgency', urgencyMedium: 'Needs attention', urgencyHigh: 'Urgent attention', urgencyUnknown: 'Not recorded', noSymptoms: 'No symptoms were recorded.'
    }
  };

  const el = {
    loading: document.querySelector('#summary-loading'), error: document.querySelector('#summary-error'), document: document.querySelector('#summary-document'),
    errorTitle: document.querySelector('#summary-error-title'), errorMessage: document.querySelector('#summary-error-message'), retry: document.querySelector('#retry-summary'), print: document.querySelector('#print-summary'),
    backResult: document.querySelector('#back-result-link'), errorResult: document.querySelector('#error-result-link'), reference: document.querySelector('#summary-reference'), date: document.querySelector('#summary-date'), status: document.querySelector('#summary-status'),
    redFlag: document.querySelector('#summary-red-flag'), redReasons: document.querySelector('#summary-red-reasons'), animalIcon: document.querySelector('#summary-animal-icon'), animalDetails: document.querySelector('#animal-details'),
    urgency: document.querySelector('#summary-urgency'), symptoms: document.querySelector('#summary-symptoms'), findings: document.querySelector('#findings-section'), noFindings: document.querySelector('#no-findings'),
    conditions: document.querySelector('#summary-conditions'), conditionsEmpty: document.querySelector('#summary-conditions-empty'), explanation: document.querySelector('#summary-explanation'), confidence: document.querySelector('#summary-confidence'),
    animalId: document.querySelector('#animal-id'), assessmentId: document.querySelector('#assessment-id')
  };

  let language = window.MaweshiI18n.getLanguage();
  let summary = null;
  let state = 'loading';
  let errorKind = null;

  function t(key) { return copy[language][key] || key; }
  function hasValue(value) { return value !== null && value !== undefined && String(value).trim() !== ''; }
  function display(value) { return hasValue(value) ? String(value) : t('notRecorded'); }
  function endpoint() { return `${API_BASE}/api/animals/${encodeURIComponent(animalId)}/assessments/${encodeURIComponent(assessmentId)}/summary`; }

  const api = {
    getSummary: () => window.MaweshiAuth.request(endpoint(), { headers: { Accept: 'application/json' } }),
    createSummary: () => window.MaweshiAuth.request(endpoint(), { method: 'POST', headers: { Accept: 'application/json' } })
  };

  function resultUrl() {
    return assessmentId && assessmentId.trim() ? `assessment-result.html?id=${encodeURIComponent(assessmentId)}` : 'index.html';
  }

  function formatDate(raw) {
    if (!hasValue(raw)) return t('notRecorded');
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) return String(raw);
    return new Intl.DateTimeFormat(language === 'ur' ? 'ur-PK' : 'en-PK', { dateStyle: 'medium', timeStyle: 'short' }).format(date);
  }

  function animalIcon(type) {
    const normalized = display(type).toLowerCase();
    if (normalized.includes('buffalo') || normalized.includes('بھینس')) return '🐃';
    if (normalized.includes('goat') || normalized.includes('بکری')) return '🐐';
    if (normalized.includes('sheep') || normalized.includes('بھیڑ')) return '🐑';
    if (normalized.includes('cow') || normalized.includes('گائے')) return '🐄';
    return '🐾';
  }

  function statusInfo(status) {
    const normalized = typeof status === 'string' ? status.toLowerCase() : 'unknown';
    const key = ['completed', 'pending', 'failed'].includes(normalized) ? normalized : 'unknown';
    return { key, label: t(`status${key[0].toUpperCase()}${key.slice(1)}`) };
  }

  function urgencyInfo(level) {
    const normalized = typeof level === 'string' ? level.toLowerCase() : 'unknown';
    const key = ['low', 'medium', 'high'].includes(normalized) ? normalized : 'unknown';
    return { key, label: t(`urgency${key[0].toUpperCase()}${key.slice(1)}`) };
  }

  function localizedDiagnosis(result) {
    const english = {
      conditions: Array.isArray(result?.possible_conditions) ? result.possible_conditions : [],
      explanation: typeof result?.explanation === 'string' ? result.explanation : '',
      confidence: typeof result?.confidence_note === 'string' ? result.confidence_note : ''
    };
    if (language !== 'ur') return english;
    const urduConditions = Array.isArray(result?.possible_conditions_urdu)
      ? result.possible_conditions_urdu.filter((item) => typeof item === 'string' && item.trim())
      : [];
    return {
      conditions: urduConditions.length ? urduConditions : english.conditions,
      explanation: typeof result?.explanation_urdu === 'string' && result.explanation_urdu.trim() ? result.explanation_urdu : english.explanation,
      confidence: typeof result?.confidence_note_urdu === 'string' && result.confidence_note_urdu.trim() ? result.confidence_note_urdu : english.confidence
    };
  }

  function addAnimalDetail(labelKey, raw, suffix = '') {
    const item = document.createElement('div');
    item.className = 'document-detail';
    const term = document.createElement('dt');
    term.textContent = t(labelKey);
    const value = document.createElement('dd');
    value.textContent = hasValue(raw) ? `${raw}${suffix}` : t('notRecorded');
    value.dir = 'auto';
    item.append(term, value);
    el.animalDetails.appendChild(item);
  }

  function renderRedFlag() {
    const active = summary.is_red_flag === true;
    el.redFlag.classList.toggle('hidden', !active);
    el.redReasons.replaceChildren();
    const reasons = Array.isArray(summary.red_flag_reasons) ? summary.red_flag_reasons.filter((reason) => typeof reason === 'string' && reason.trim()) : [];
    reasons.forEach((reason) => {
      const item = document.createElement('li');
      item.textContent = reason;
      item.dir = 'auto';
      el.redReasons.appendChild(item);
    });
  }

  function renderDocument() {
    const animal = summary.animal && typeof summary.animal === 'object' ? summary.animal : {};
    const diagnosis = summary.diagnosis_result && typeof summary.diagnosis_result === 'object' ? summary.diagnosis_result : null;
    const localized = localizedDiagnosis(diagnosis);
    const status = statusInfo(summary.status);
    const urgency = urgencyInfo(diagnosis?.urgency_level);

    el.reference.textContent = display(summary.id);
    el.date.textContent = formatDate(summary.created_at);
    el.status.className = `document-status document-status--${status.key}`;
    el.status.textContent = status.label;
    el.animalIcon.textContent = animalIcon(animal.animal_type);
    el.animalDetails.replaceChildren();
    addAnimalDetail('animalName', animal.name);
    addAnimalDetail('animalType', animal.animal_type);
    addAnimalDetail('breed', animal.breed);
    addAnimalDetail('gender', animal.gender);
    addAnimalDetail('age', animal.age, hasValue(animal.age) ? ` ${t('years')}` : '');
    addAnimalDetail('weight', animal.weight, hasValue(animal.weight) ? ` ${t('kg')}` : '');
    addAnimalDetail('color', animal.color);
    addAnimalDetail('healthStatus', animal.health_status);

    el.urgency.className = `document-urgency document-urgency--${urgency.key}`;
    el.urgency.textContent = urgency.label;
    el.symptoms.textContent = hasValue(summary.symptoms) ? summary.symptoms : t('noSymptoms');
    el.animalId.textContent = display(summary.animal_id);
    el.assessmentId.textContent = display(summary.assessment_id);
    renderRedFlag();

    const hasDiagnosis = diagnosis && (localized.conditions.length || hasValue(localized.explanation) || hasValue(localized.confidence));
    el.findings.classList.toggle('hidden', !hasDiagnosis);
    el.noFindings.classList.toggle('hidden', hasDiagnosis);
    if (hasDiagnosis) {
      const conditions = localized.conditions.filter((condition) => typeof condition === 'string' && condition.trim());
      el.conditions.replaceChildren();
      conditions.forEach((condition) => {
        const item = document.createElement('li');
        item.textContent = condition;
        item.dir = 'auto';
        el.conditions.appendChild(item);
      });
      el.conditions.classList.toggle('hidden', conditions.length === 0);
      el.conditionsEmpty.classList.toggle('hidden', conditions.length !== 0);
      el.explanation.textContent = display(localized.explanation);
      el.confidence.textContent = display(localized.confidence);
    }
    document.title = `${display(animal.name)} | ${t('pageTitle')} | Maweshi Muhafiz`;
  }

  function render() {
    el.loading.classList.toggle('hidden', state !== 'loading');
    el.error.classList.toggle('hidden', state !== 'error');
    el.document.classList.toggle('hidden', state !== 'ready');
    el.print.classList.toggle('hidden', state !== 'ready');
    if (state === 'error') {
      el.errorTitle.textContent = t(`${errorKind}Title`);
      el.errorMessage.textContent = t(`${errorKind}Message`);
      el.retry.classList.toggle('hidden', errorKind === 'missing' || errorKind === 'notFound');
    }
    if (state === 'ready') renderDocument();
  }

  function isSummaryMissing(error) {
    const detail = `${error?.message || ''} ${error?.details || ''}`;
    return error?.status === 404 && detail.includes('Vet case summary not found for this assessment.');
  }

  async function loadSummary() {
    if (!animalId || !animalId.trim() || !assessmentId || !assessmentId.trim()) {
      state = 'error'; errorKind = 'missing'; render(); return;
    }
    state = 'loading'; errorKind = null; render();
    try {
      try {
        summary = await api.getSummary();
        if (!summary?.animal || typeof summary.animal !== 'object') summary = await api.createSummary();
      }
      catch (error) {
        if (!isSummaryMissing(error)) throw error;
        summary = await api.createSummary();
      }
      if (!summary || typeof summary !== 'object' || !summary.animal || typeof summary.animal !== 'object') {
        state = 'error'; errorKind = 'malformed'; render(); return;
      }
      state = 'ready'; render();
    } catch (error) {
      console.error('Vet-ready summary could not be loaded.', error);
      state = 'error';
      errorKind = error.status === 404 ? 'notFound' : error.status === 403 ? 'forbidden' : 'connection';
      render();
    }
  }

  function applyLanguage(nextLanguage) {
    language = window.MaweshiI18n.applyPage(nextLanguage, copy).language;
    render();
  }

  const destination = resultUrl();
  el.backResult.href = destination;
  el.errorResult.href = destination;
  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) applyLanguage(languageButton.dataset.language);
  });
  el.retry.addEventListener('click', loadSummary);
  el.print.addEventListener('click', () => window.print());

  applyLanguage(language);
  loadSummary();
})();
