(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const params = new URLSearchParams(window.location.search);
  const animalId = params.get('id');
  const assessmentId1 = params.get('assessment1');
  const assessmentId2 = params.get('assessment2');

  const copy = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں', logout: 'لاگ آؤٹ', backToHistory: 'صحت کی پچھلی تفصیل پر واپس جائیں', loadingLabel: 'معائنوں کا موازنہ دیکھا جا رہا ہے',
      comparisonKicker: 'دو صحت معائنے', comparisonTitle: 'صحت کے معائنوں کا موازنہ', comparisonSubtitle: 'وقت کے ساتھ درج کی گئی علامات اور رہنمائی ساتھ دیکھیں۔', cautionLabel: 'اہم وضاحت', noVerdict: 'یہ دونوں ریکارڈ صرف ساتھ دکھائے گئے ہیں۔ مویشی محافظ نے یہ فیصلہ نہیں کیا کہ حالت بہتر ہوئی یا خراب۔', comparisonGridLabel: 'دو صحت معائنوں کی معلومات',
      earlierAssessment: 'پہلا معائنہ', laterAssessment: 'بعد کا معائنہ', statusCompleted: 'مکمل', statusPending: 'جاری ہے', statusFailed: 'مکمل نہیں ہوا', statusUnknown: 'حالت درج نہیں', urgencyLow: 'کم فوری توجہ', urgencyMedium: 'توجہ درکار', urgencyHigh: 'فوری توجہ', redFlag: 'خطرے کی علامت',
      reportedSymptoms: 'بتائی گئی علامات', possibleConditions: 'ممکنہ حالتیں', explanation: 'وضاحت', confidence: 'ضروری احتیاط', safeNextSteps: 'محفوظ اگلے قدم', redFlagReasons: 'فوری توجہ کی وجوہات', noSymptoms: 'کوئی علامات درج نہیں', noConditions: 'کوئی ممکنہ حالت درج نہیں', unavailable: 'اس معائنے میں یہ معلومات موجود نہیں۔',
      imageLoading: 'تصویر دیکھی جا رہی ہے…', imageUnavailable: 'اس معائنے کی تصویر دستیاب نہیں۔', earlierImageAlt: 'پہلے صحت معائنے کی جانور کی تصویر', laterImageAlt: 'بعد کے صحت معائنے کی جانور کی تصویر', dateUnavailable: 'تاریخ درج نہیں', viewResult: 'مکمل نتیجہ دیکھیں',
      pendingMessage: 'یہ معائنہ ابھی مکمل ہو رہا ہے۔ مکمل نتیجہ ابھی دستیاب نہیں۔', failedMessage: 'یہ معائنہ مکمل نہیں ہو سکا۔',
      missingTitle: 'موازنہ شروع نہیں ہو سکا', missingMessage: 'صحت کی پچھلی تفصیل سے دو الگ معائنے منتخب کریں۔', invalidTitle: 'یہ دونوں معائنے نہیں دکھائے جا سکتے', invalidMessage: 'براہِ کرم اسی جانور کے دو درست معائنے دوبارہ منتخب کریں۔', notFoundTitle: 'معائنوں کا ریکارڈ نہیں ملا', notFoundMessage: 'منتخب معائنوں میں سے کوئی ریکارڈ موجود نہیں یا ہٹا دیا گیا ہے۔', forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ ریکارڈ دیکھنے کی اجازت نہیں ہے۔', connectionTitle: 'موازنہ ابھی دستیاب نہیں', connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔', malformedTitle: 'موازنہ مکمل نہیں دکھایا جا سکتا', malformedMessage: 'منتخب ریکارڈ کی معلومات سمجھ نہیں آئیں۔ براہِ کرم دوبارہ کوشش کریں۔', tryAgain: 'دوبارہ کوشش کریں',
      footerCare: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔', footerDisclaimer: 'AI کی رائے ابتدائی رہنمائی ہے، ڈاکٹر کا متبادل نہیں۔'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language', logout: 'Logout', backToHistory: 'Back to Health History', loadingLabel: 'Loading assessment comparison',
      comparisonKicker: 'Two health assessments', comparisonTitle: 'Health Assessment Comparison', comparisonSubtitle: 'Review recorded symptoms and guidance side by side over time.', cautionLabel: 'Important clarification', noVerdict: 'These two records are shown side by side only. MaweshiMuhafiz has not judged whether the condition improved or worsened.', comparisonGridLabel: 'Two health assessment records',
      earlierAssessment: 'Earlier Assessment', laterAssessment: 'Later Assessment', statusCompleted: 'Completed', statusPending: 'Pending', statusFailed: 'Not completed', statusUnknown: 'Status unavailable', urgencyLow: 'Low urgency', urgencyMedium: 'Needs attention', urgencyHigh: 'Urgent attention', redFlag: 'Red flag',
      reportedSymptoms: 'Reported Symptoms', possibleConditions: 'Possible Conditions', explanation: 'Explanation', confidence: 'What to Keep in Mind', safeNextSteps: 'Safe Next Steps', redFlagReasons: 'Reasons for Urgent Attention', noSymptoms: 'No symptoms recorded', noConditions: 'No possible condition recorded', unavailable: 'This information is not available for this assessment.',
      imageLoading: 'Loading assessment image…', imageUnavailable: 'No assessment image is available.', earlierImageAlt: 'Animal image from the earlier health assessment', laterImageAlt: 'Animal image from the later health assessment', dateUnavailable: 'Date not recorded', viewResult: 'View Full Result',
      pendingMessage: 'This assessment is still being completed. A full result is not available yet.', failedMessage: 'This assessment could not be completed.',
      missingTitle: 'Comparison could not start', missingMessage: 'Select two different assessments from Health History.', invalidTitle: 'These assessments cannot be compared', invalidMessage: 'Please select two valid assessments for the same animal again.', notFoundTitle: 'Assessment records not found', notFoundMessage: 'One of the selected assessment records does not exist or may have been removed.', forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to access this record.', connectionTitle: 'Comparison unavailable right now', connectionMessage: 'We could not connect. Please try again in a little while.', malformedTitle: 'Comparison cannot be shown completely', malformedMessage: 'The selected record information could not be understood. Please try again.', tryAgain: 'Try again',
      footerCare: 'Built to support better livestock care.', footerDisclaimer: 'AI guidance is preliminary and does not replace a veterinarian.'
    }
  };

  const el = {
    loading: document.querySelector('#compare-loading'), error: document.querySelector('#compare-error'), page: document.querySelector('#compare-page'), grid: document.querySelector('#comparison-grid'),
    errorTitle: document.querySelector('#compare-error-title'), errorMessage: document.querySelector('#compare-error-message'), retry: document.querySelector('#retry-compare'),
    historyLink: document.querySelector('#history-link'), errorHistoryLink: document.querySelector('#error-history-link'), animalSummary: document.querySelector('#animal-summary')
  };

  let language = window.MaweshiI18n.getLanguage();
  let state = 'loading';
  let errorKind = null;
  let records = [];
  let animal = null;
  const imageStates = new Map();

  function t(key) { return copy[language][key] || key; }
  function clean(value) { return typeof value === 'string' ? value.trim() : ''; }
  function safeTime(raw) { const value = new Date(raw || 0).getTime(); return Number.isNaN(value) ? 0 : value; }
  function validId(value) { return value !== null && value !== undefined && String(value).trim() !== ''; }
  function validRecord(record) { return record && typeof record === 'object' && validId(record.id) && String(record.animal_id) === String(animalId); }

  const api = {
    compare: (id, first, second) => {
      const query = new URLSearchParams({ assessment_id_1: first, assessment_id_2: second });
      return window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/assessments/compare?${query.toString()}`, { headers: { Accept: 'application/json' } });
    },
    getAnimal: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, { headers: { Accept: 'application/json' } }),
    getImage: (id) => window.MaweshiAuth.requestBlob(`${API_BASE}/api/images/${encodeURIComponent(id)}`, { headers: { Accept: 'image/*' } })
  };

  function setHistoryLinks() {
    const destination = validId(animalId) ? `health-history.html?id=${encodeURIComponent(animalId)}` : 'dashboard.html';
    el.historyLink.href = destination;
    el.errorHistoryLink.href = destination;
  }

  function formatDate(raw) {
    const date = new Date(raw || 0);
    if (!raw || Number.isNaN(date.getTime())) return t('dateUnavailable');
    return new Intl.DateTimeFormat(language === 'ur' ? 'ur-PK' : 'en-PK', { dateStyle: 'medium', timeStyle: 'short' }).format(date);
  }

  function statusOf(record) { return ['completed', 'pending', 'failed'].includes(record.status) ? record.status : 'unknown'; }
  function urgencyOf(record) {
    const result = record.diagnosis_result;
    return statusOf(record) === 'completed' && result && typeof result === 'object' && ['low', 'medium', 'high'].includes(result.urgency_level) ? result.urgency_level : null;
  }
  function statusLabel(status) { return t(status === 'completed' ? 'statusCompleted' : status === 'pending' ? 'statusPending' : status === 'failed' ? 'statusFailed' : 'statusUnknown'); }
  function urgencyLabel(urgency) { return t(urgency === 'low' ? 'urgencyLow' : urgency === 'high' ? 'urgencyHigh' : 'urgencyMedium'); }

  function localizedField(result, englishKey, urduKey) {
    if (!result || typeof result !== 'object') return null;
    if (language === 'ur') {
      const urdu = result[urduKey];
      if (Array.isArray(urdu) ? urdu.length : clean(urdu)) return urdu;
    }
    return result[englishKey];
  }

  function usableStrings(value) {
    if (Array.isArray(value)) return value.filter((item) => typeof item === 'string' && item.trim());
    return [];
  }

  function chip(text, modifier, icon) {
    const node = document.createElement('span');
    node.className = `comparison-chip comparison-chip--${modifier}`;
    node.textContent = `${icon} ${text}`;
    return node;
  }

  function addTextField(container, titleKey, value, modifier = '') {
    const text = clean(value);
    if (!text) return false;
    const section = document.createElement('section');
    section.className = `comparison-field${modifier ? ` comparison-field--${modifier}` : ''}`;
    const heading = document.createElement('h3'); heading.textContent = t(titleKey);
    const paragraph = document.createElement('p'); paragraph.textContent = text; paragraph.dir = 'auto';
    section.append(heading, paragraph); container.appendChild(section);
    return true;
  }

  function addListField(container, titleKey, values, modifier = '') {
    const items = usableStrings(values);
    if (!items.length) return false;
    const section = document.createElement('section');
    section.className = `comparison-field${modifier ? ` comparison-field--${modifier}` : ''}`;
    const heading = document.createElement('h3'); heading.textContent = t(titleKey);
    const list = document.createElement('ul');
    items.forEach((value) => { const item = document.createElement('li'); item.textContent = value; item.dir = 'auto'; list.appendChild(item); });
    section.append(heading, list); container.appendChild(section);
    return true;
  }

  function createImageArea(record, position) {
    const wrapper = document.createElement('div'); wrapper.className = 'assessment-image';
    const firstImageId = Array.isArray(record.image_ids) ? record.image_ids.find(validId) : null;
    const stored = imageStates.get(String(record.id));
    if (stored?.status === 'loaded' && stored.url) {
      const image = document.createElement('img'); image.src = stored.url; image.alt = t(position === 'earlier' ? 'earlierImageAlt' : 'laterImageAlt'); wrapper.appendChild(image); return wrapper;
    }
    const statusNode = document.createElement('div'); statusNode.className = 'assessment-image-state';
    const messageKey = firstImageId && stored?.status !== 'unavailable' ? 'imageLoading' : 'imageUnavailable';
    statusNode.innerHTML = `<div><span aria-hidden="true">${messageKey === 'imageLoading' ? '…' : '▧'}</span><p>${t(messageKey)}</p></div>`;
    wrapper.appendChild(statusNode);
    return wrapper;
  }

  function createColumn(record, position) {
    const status = statusOf(record);
    const urgency = urgencyOf(record);
    const result = record.diagnosis_result && typeof record.diagnosis_result === 'object' ? record.diagnosis_result : null;
    const column = document.createElement('article'); column.className = 'assessment-column';

    const head = document.createElement('header'); head.className = 'assessment-column-head';
    const identity = document.createElement('div');
    const label = document.createElement('p'); label.className = 'assessment-position'; label.textContent = t(position === 'earlier' ? 'earlierAssessment' : 'laterAssessment');
    const date = document.createElement('time'); date.dateTime = record.created_at || ''; date.textContent = formatDate(record.created_at);
    identity.append(label, date);
    const badges = document.createElement('div'); badges.className = 'assessment-badges';
    badges.appendChild(chip(statusLabel(status), status, status === 'completed' ? '✓' : status === 'pending' ? '…' : status === 'failed' ? '!' : '–'));
    if (urgency) badges.appendChild(chip(urgencyLabel(urgency), urgency, urgency === 'low' ? '✓' : '!'));
    if (record.is_red_flag === true) badges.appendChild(chip(t('redFlag'), 'red-flag', '!'));
    head.append(identity, badges);

    const details = document.createElement('div'); details.className = 'assessment-details';
    addTextField(details, 'reportedSymptoms', clean(record.symptoms) || t('noSymptoms'));

    if (status === 'pending' || status === 'failed') {
      const message = document.createElement('p'); message.className = 'record-unavailable'; message.textContent = t(status === 'pending' ? 'pendingMessage' : 'failedMessage'); details.appendChild(message);
    } else {
      const conditions = localizedField(result, 'possible_conditions', 'possible_conditions_urdu');
      addListField(details, 'possibleConditions', conditions);
      addTextField(details, 'explanation', localizedField(result, 'explanation', 'explanation_urdu'));
      addTextField(details, 'confidence', localizedField(result, 'confidence_note', 'confidence_note_urdu'));
      const safeSteps = localizedField(result, 'safe_next_steps', 'safe_next_steps_urdu');
      if (Array.isArray(safeSteps)) addListField(details, 'safeNextSteps', safeSteps);
      else addTextField(details, 'safeNextSteps', safeSteps);
      if (!result) {
        const message = document.createElement('p'); message.className = 'record-unavailable'; message.textContent = t('unavailable'); details.appendChild(message);
      }
    }

    if (record.is_red_flag === true) addListField(details, 'redFlagReasons', record.red_flag_reasons, 'red-flag');

    const resultLink = document.createElement('a');
    resultLink.className = 'view-record-link'; resultLink.href = `assessment-result.html?id=${encodeURIComponent(record.id)}`; resultLink.textContent = t('viewResult');
    column.append(head, createImageArea(record, position), details, resultLink);
    return column;
  }

  function render() {
    el.loading.classList.toggle('hidden', state !== 'loading');
    el.error.classList.toggle('hidden', state !== 'error');
    el.page.classList.toggle('hidden', state !== 'ready');
    if (state === 'error') {
      el.errorTitle.textContent = t(`${errorKind}Title`);
      el.errorMessage.textContent = t(`${errorKind}Message`);
      el.retry.classList.toggle('hidden', errorKind === 'missing' || errorKind === 'notFound');
      return;
    }
    if (state !== 'ready') return;
    el.animalSummary.textContent = animal && typeof animal === 'object' ? [animal.name, animal.animal_type].filter((value) => clean(String(value ?? ''))).join(' · ') : '';
    el.grid.replaceChildren(createColumn(records[0], 'earlier'), createColumn(records[1], 'later'));
    document.title = `${t('comparisonTitle')} | Maweshi Muhafiz`;
  }

  async function loadImage(record) {
    const imageIds = Array.isArray(record.image_ids) ? record.image_ids.filter(validId) : [];
    if (!imageIds.length) { imageStates.set(String(record.id), { status: 'none' }); return; }
    imageStates.set(String(record.id), { status: 'loading' });
    for (const imageId of imageIds) {
      try {
        const blob = await api.getImage(imageId);
        if (!blob || !blob.type.startsWith('image/')) throw new Error('Unsupported image response');
        imageStates.set(String(record.id), { status: 'loaded', url: URL.createObjectURL(blob) });
        if (state === 'ready') render();
        return;
      } catch (error) {
        console.error('Assessment image could not be loaded.', error);
        if (error.status === 401) break;
      }
    }
    imageStates.set(String(record.id), { status: 'unavailable' });
    if (state === 'ready') render();
  }

  async function loadComparison() {
    if (![animalId, assessmentId1, assessmentId2].every(validId) || String(assessmentId1) === String(assessmentId2)) {
      state = 'error'; errorKind = 'missing'; render(); return;
    }
    state = 'loading'; errorKind = null; render();
    try {
      const [comparison, animalResult] = await Promise.all([
        api.compare(animalId, assessmentId1, assessmentId2),
        api.getAnimal(animalId).catch((error) => { console.error('Animal heading could not be loaded.', error); return null; })
      ]);
      if (!comparison || typeof comparison !== 'object' || !validRecord(comparison.assessment_1) || !validRecord(comparison.assessment_2)) {
        state = 'error'; errorKind = 'malformed'; render(); return;
      }
      records = [comparison.assessment_1, comparison.assessment_2].sort((a, b) => safeTime(a.created_at) - safeTime(b.created_at));
      animal = animalResult;
      state = 'ready'; render();
      records.forEach((record) => { loadImage(record); });
    } catch (error) {
      console.error('Assessment comparison could not be loaded.', error);
      state = 'error';
      errorKind = error.status === 400 ? 'invalid' : error.status === 404 ? 'notFound' : error.status === 403 ? 'forbidden' : 'connection';
      render();
    }
  }

  function applyLanguage(nextLanguage) {
    language = window.MaweshiI18n.applyPage(nextLanguage, copy).language;
    render();
  }

  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) applyLanguage(languageButton.dataset.language);
  });
  el.retry.addEventListener('click', loadComparison);
  window.addEventListener('beforeunload', () => imageStates.forEach((value) => { if (value.url) URL.revokeObjectURL(value.url); }));

  setHistoryLinks();
  applyLanguage(language);
  loadComparison();
})();
