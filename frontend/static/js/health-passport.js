(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const animalId = new URLSearchParams(window.location.search).get('id');

  const copy = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں', logout: 'لاگ آؤٹ', backToProfile: 'جانور کے پروفائل پر واپس جائیں',
      loadingLabel: 'صحت پاسپورٹ دیکھا جا رہا ہے', tryAgain: 'دوبارہ کوشش کریں', missingTitle: 'جانور منتخب نہیں کیا گیا', missingMessage: 'صحت پاسپورٹ دیکھنے کے لیے درست جانور منتخب کریں۔',
      notFoundTitle: 'صحت پاسپورٹ نہیں ملا', notFoundMessage: 'یہ جانور موجود نہیں یا دستیاب نہیں رہا۔', forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ صحت ریکارڈ دیکھنے کی اجازت نہیں ہے۔',
      connectionTitle: 'صحت پاسپورٹ ابھی دستیاب نہیں', connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔', malformedTitle: 'صحت پاسپورٹ مکمل نہیں', malformedMessage: 'اس ریکارڈ کی مکمل معلومات ابھی نہیں دکھائی جا سکتیں۔',
      digitalPassport: 'ڈیجیٹل جانور صحت پاسپورٹ', passportPurpose: 'جانور کی صحت، معائنوں اور دیکھ بھال کی منظم تفصیل۔', animalType: 'جانور کی قسم', breed: 'نسل', age: 'عمر', weight: 'وزن', color: 'رنگ', gender: 'جنس', region: 'علاقہ', healthStatus: 'موجودہ صحت',
      notRecorded: 'درج نہیں', female: 'مادہ', male: 'نر', healthy: 'صحت مند', needsAttention: 'توجہ درکار', underTreatment: 'علاج جاری ہے', year: 'سال', kg: 'کلو',
      healthRecord: 'صحت کا ریکارڈ', healthOverview: 'صحت کا خلاصہ', totalAssessments: 'کل صحت معائنے', latestAssessment: 'تازہ ترین معائنہ', noAssessmentYet: 'ابھی کوئی معائنہ نہیں',
      longTermRecord: 'مسلسل صحت ریکارڈ', assessmentHistory: 'معائنوں کی تفصیل', viewFullHistory: 'مکمل تفصیل دیکھیں', noAssessments: 'ابھی تک صحت کا کوئی معائنہ موجود نہیں ہے۔', viewResult: 'نتیجہ دیکھیں',
      statusCompleted: 'مکمل', statusPending: 'جاری ہے', statusFailed: 'مکمل نہیں ہوا', urgencyLow: 'کم فوری توجہ', urgencyMedium: 'توجہ درکار', urgencyHigh: 'فوری توجہ', urgencyUnknown: 'فوری توجہ درج نہیں', noCondition: 'کوئی ممکنہ بیماری درج نہیں',
      carePlanning: 'دیکھ بھال کی منصوبہ بندی', preventiveCare: 'بیماری سے بچاؤ کی یاددہانی', manageReminders: 'یاددہانی سنبھالیں', upcoming: 'آنے والی', past: 'گزری ہوئی', noUpcomingReminders: 'کوئی آنے والی یاددہانی نہیں۔', noPastReminders: 'کوئی گزری ہوئی یاددہانی نہیں۔', dueDate: 'تاریخ', noNotes: 'کوئی نوٹ درج نہیں',
      vetRecords: 'ڈاکٹر کے لیے ریکارڈ', vetSummaries: 'ڈاکٹر کے لیے خلاصے', noSummaries: 'ابھی ڈاکٹر کے لیے کوئی خلاصہ موجود نہیں ہے۔', vetSummary: 'ڈاکٹر کے لیے صحت کا خلاصہ', viewSummary: 'خلاصہ دیکھیں',
      footerCare: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔', privateRecord: 'یہ کسان کا ذاتی صحت ریکارڈ ہے۔'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language', logout: 'Logout', backToProfile: 'Back to Animal Profile',
      loadingLabel: 'Loading health passport', tryAgain: 'Try again', missingTitle: 'No animal selected', missingMessage: 'Select a valid animal to view its Health Passport.',
      notFoundTitle: 'Health Passport not found', notFoundMessage: 'This animal does not exist or is no longer available.', forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to view this health record.',
      connectionTitle: 'Health Passport unavailable right now', connectionMessage: 'We could not connect. Please try again in a little while.', malformedTitle: 'Health Passport is incomplete', malformedMessage: 'Complete information for this record cannot be shown right now.',
      digitalPassport: 'Digital Animal Health Passport', passportPurpose: 'An organised record of this animal’s health, assessments and care.', animalType: 'Animal type', breed: 'Breed', age: 'Age', weight: 'Weight', color: 'Color', gender: 'Gender', region: 'Region', healthStatus: 'Current health',
      notRecorded: 'Not recorded', female: 'Female', male: 'Male', healthy: 'Healthy', needsAttention: 'Needs attention', underTreatment: 'Under treatment', year: 'yr', kg: 'kg',
      healthRecord: 'Health record', healthOverview: 'Health overview', totalAssessments: 'Total health assessments', latestAssessment: 'Latest assessment', noAssessmentYet: 'No assessments yet',
      longTermRecord: 'Long-term record', assessmentHistory: 'Assessment history', viewFullHistory: 'View full history', noAssessments: 'No health assessments yet.', viewResult: 'View Result',
      statusCompleted: 'Completed', statusPending: 'Pending', statusFailed: 'Not completed', urgencyLow: 'Low urgency', urgencyMedium: 'Needs attention', urgencyHigh: 'Urgent attention', urgencyUnknown: 'Urgency not recorded', noCondition: 'No possible condition recorded',
      carePlanning: 'Care planning', preventiveCare: 'Preventive Care Reminders', manageReminders: 'Manage reminders', upcoming: 'Upcoming', past: 'Past', noUpcomingReminders: 'No upcoming reminders.', noPastReminders: 'No past reminders.', dueDate: 'Due', noNotes: 'No notes recorded',
      vetRecords: 'Veterinary records', vetSummaries: 'Vet-Ready Summaries', noSummaries: 'No Vet-Ready Summaries yet.', vetSummary: 'Vet-Ready health summary', viewSummary: 'View Summary',
      footerCare: 'Built to support better livestock care.', privateRecord: 'This is the farmer’s private health record.'
    }
  };

  const el = {
    loading: document.querySelector('#passport-loading'), error: document.querySelector('#passport-error'), page: document.querySelector('#passport-page'),
    errorTitle: document.querySelector('#passport-error-title'), errorMessage: document.querySelector('#passport-error-message'), retry: document.querySelector('#retry-passport'),
    name: document.querySelector('#animal-name'), kind: document.querySelector('#animal-kind'), icon: document.querySelector('#animal-icon'), healthBadge: document.querySelector('#health-badge'),
    type: document.querySelector('#fact-type'), breed: document.querySelector('#fact-breed'), age: document.querySelector('#fact-age'), weight: document.querySelector('#fact-weight'), gender: document.querySelector('#fact-gender'), color: document.querySelector('#fact-color'), region: document.querySelector('#fact-region'), health: document.querySelector('#fact-health'),
    assessmentCount: document.querySelector('#assessment-count'), latestAssessment: document.querySelector('#latest-assessment'), assessments: document.querySelector('#assessments-list'), assessmentsEmpty: document.querySelector('#assessments-empty'),
    upcoming: document.querySelector('#upcoming-list'), upcomingEmpty: document.querySelector('#upcoming-empty'), past: document.querySelector('#past-list'), pastEmpty: document.querySelector('#past-empty'),
    summaries: document.querySelector('#summaries-list'), summariesEmpty: document.querySelector('#summaries-empty'), profileLink: document.querySelector('#profile-link'), errorProfileLink: document.querySelector('#error-profile-link'),
    historyLink: document.querySelector('#full-history-link'), preventiveLink: document.querySelector('#preventive-care-link')
  };

  let language = window.MaweshiI18n.getLanguage();
  let passport = null;
  let errorKind = null;

  function t(key) { return copy[language][key] || key; }
  function text(value, fallback = t('notRecorded')) { return value === null || value === undefined || String(value).trim() === '' ? fallback : String(value); }
  function stringList(value) { return Array.isArray(value) ? value.filter((item) => typeof item === 'string' && item.trim()) : []; }
  function translatedValue(value) { return { Female: t('female'), Male: t('male'), Healthy: t('healthy'), 'Needs attention': t('needsAttention'), 'Under treatment': t('underTreatment') }[value] || text(value); }
  function formatDate(raw) {
    if (!raw) return t('notRecorded');
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) return t('notRecorded');
    return new Intl.DateTimeFormat(language === 'ur' ? 'ur-PK' : 'en-PK', { day: 'numeric', month: 'short', year: 'numeric' }).format(date);
  }
  function dateValue(raw) { const value = new Date(raw || 0).getTime(); return Number.isNaN(value) ? 0 : value; }
  function animalIcon(type) {
    const normalized = text(type, '').toLowerCase();
    if (normalized.includes('buffalo') || normalized.includes('بھینس')) return '🐃';
    if (normalized.includes('goat') || normalized.includes('بکری') || normalized.includes('بکرا')) return '🐐';
    if (normalized.includes('sheep') || normalized.includes('بھیڑ') || normalized.includes('دنبہ')) return '🐑';
    if (normalized.includes('cow') || normalized.includes('cattle') || normalized.includes('گائے') || normalized.includes('بیل')) return '🐄';
    return '🐾';
  }
  function healthClass(raw) {
    const status = text(raw, '').toLowerCase();
    if (['healthy', 'good', 'fit'].includes(status)) return 'health-badge--healthy';
    if (status.includes('attention') || status.includes('treatment') || status.includes('sick') || status.includes('critical')) return 'health-badge--attention';
    return 'health-badge--unknown';
  }
  function statusLabel(status) { return t(status === 'completed' ? 'statusCompleted' : status === 'failed' ? 'statusFailed' : 'statusPending'); }
  function urgencyLabel(level) { return t(level === 'high' ? 'urgencyHigh' : level === 'medium' ? 'urgencyMedium' : level === 'low' ? 'urgencyLow' : 'urgencyUnknown'); }
  function diagnosis(record) { return record?.diagnosis_result && typeof record.diagnosis_result === 'object' ? record.diagnosis_result : {}; }
  function localizedConditions(result) {
    const english = stringList(result.possible_conditions);
    if (language !== 'ur') return english;
    const urdu = stringList(result.possible_conditions_urdu);
    return urdu.length ? urdu : english;
  }

  function setLinks() {
    const profile = animalId ? `animal-profile.html?id=${encodeURIComponent(animalId)}` : 'index.html';
    el.profileLink.href = profile;
    el.errorProfileLink.href = profile;
    el.historyLink.href = animalId ? `health-history.html?id=${encodeURIComponent(animalId)}` : profile;
    el.preventiveLink.href = animalId ? `preventive-care.html?id=${encodeURIComponent(animalId)}` : profile;
  }

  function renderAnimal(animal) {
    el.name.textContent = text(animal.name);
    el.kind.textContent = [text(animal.animal_type, ''), text(animal.breed, '')].filter(Boolean).join(' · ') || t('notRecorded');
    el.icon.textContent = animalIcon(animal.animal_type);
    el.healthBadge.className = `health-badge ${healthClass(animal.health_status)}`;
    el.healthBadge.textContent = translatedValue(animal.health_status);
    el.type.textContent = text(animal.animal_type);
    el.breed.textContent = text(animal.breed);
    el.age.textContent = animal.age === null || animal.age === undefined ? t('notRecorded') : `${animal.age} ${t('year')}`;
    el.weight.textContent = animal.weight === null || animal.weight === undefined ? t('notRecorded') : `${animal.weight} ${t('kg')}`;
    el.gender.textContent = translatedValue(animal.gender);
    el.color.textContent = text(animal.color);
    el.region.textContent = text(animal.region);
    el.health.textContent = translatedValue(animal.health_status);
    document.title = `${text(animal.name)} | ${t('digitalPassport')} | Maweshi Muhafiz`;
  }

  function renderOverview(records) {
    const sorted = [...records].sort((a, b) => dateValue(b.created_at) - dateValue(a.created_at));
    el.assessmentCount.textContent = String(records.length);
    if (!sorted.length) { el.latestAssessment.textContent = t('noAssessmentYet'); return; }
    const latest = sorted[0];
    const result = diagnosis(latest);
    const detail = latest.status === 'completed' && result.urgency_level ? urgencyLabel(result.urgency_level) : statusLabel(latest.status);
    el.latestAssessment.textContent = `${formatDate(latest.created_at)} · ${detail}`;
  }

  function renderAssessments(records) {
    const sorted = [...records].sort((a, b) => dateValue(b.created_at) - dateValue(a.created_at));
    el.assessments.replaceChildren();
    el.assessmentsEmpty.classList.toggle('hidden', sorted.length !== 0);
    sorted.forEach((record) => {
      const result = diagnosis(record);
      const urgency = ['low', 'medium', 'high'].includes(result.urgency_level) ? result.urgency_level : 'unknown';
      const conditions = localizedConditions(result);
      const article = document.createElement('article'); article.className = 'passport-record';
      const top = document.createElement('div'); top.className = 'record-top';
      const date = document.createElement('time'); date.dateTime = record.created_at || ''; date.textContent = formatDate(record.created_at);
      const badges = document.createElement('div'); badges.className = 'record-badges';
      const status = document.createElement('span'); status.className = `passport-chip passport-chip--${record.status || 'pending'}`; status.textContent = statusLabel(record.status);
      badges.appendChild(status);
      if (record.status === 'completed' && urgency !== 'unknown') {
        const urgencyBadge = document.createElement('span'); urgencyBadge.className = `passport-chip passport-chip--${urgency}`; urgencyBadge.textContent = urgencyLabel(urgency); badges.appendChild(urgencyBadge);
      }
      top.append(date, badges);
      const title = document.createElement('h3'); title.className = 'record-title'; title.dir = 'auto'; title.textContent = conditions.join('، ') || t('noCondition');
      const symptoms = document.createElement('p'); symptoms.className = 'record-copy'; symptoms.dir = 'auto'; symptoms.textContent = text(record.symptoms);
      article.append(top, title, symptoms);
      if (record.id !== null && record.id !== undefined && String(record.id).trim()) {
        const link = document.createElement('a'); link.className = 'record-link'; link.href = `assessment-result.html?id=${encodeURIComponent(record.id)}`; link.textContent = t('viewResult'); article.appendChild(link);
      }
      el.assessments.appendChild(article);
    });
  }

  function renderReminderList(container, empty, records, direction) {
    const sorted = [...records].sort((a, b) => direction * (dateValue(a.due_date) - dateValue(b.due_date)));
    container.replaceChildren();
    empty.classList.toggle('hidden', sorted.length !== 0);
    sorted.forEach((record) => {
      const article = document.createElement('article'); article.className = 'reminder-record';
      const title = document.createElement('strong'); title.dir = 'auto'; title.textContent = text(record.reminder_type);
      const date = document.createElement('time'); date.className = 'reminder-date'; date.dateTime = record.due_date || ''; date.textContent = `${t('dueDate')}: ${formatDate(record.due_date)}`;
      article.append(title, date);
      if (record.notes && String(record.notes).trim()) { const notes = document.createElement('p'); notes.className = 'reminder-notes'; notes.dir = 'auto'; notes.textContent = record.notes; article.appendChild(notes); }
      container.appendChild(article);
    });
  }

  function renderSummaries(records) {
    const sorted = [...records].sort((a, b) => dateValue(b.created_at) - dateValue(a.created_at));
    el.summaries.replaceChildren();
    el.summariesEmpty.classList.toggle('hidden', sorted.length !== 0);
    sorted.forEach((record) => {
      const result = diagnosis(record);
      const article = document.createElement('article'); article.className = 'summary-record';
      const top = document.createElement('div'); top.className = 'record-top';
      const date = document.createElement('time'); date.dateTime = record.created_at || ''; date.textContent = formatDate(record.created_at);
      const badge = document.createElement('span'); badge.className = `passport-chip passport-chip--${record.is_red_flag ? 'high' : record.status || 'unknown'}`; badge.textContent = record.is_red_flag ? urgencyLabel('high') : statusLabel(record.status);
      top.append(date, badge);
      const title = document.createElement('h3'); title.className = 'record-title'; title.textContent = t('vetSummary');
      const conditions = localizedConditions(result);
      const detail = document.createElement('p'); detail.className = 'record-copy'; detail.dir = 'auto'; detail.textContent = conditions.join('، ') || t('noCondition');
      article.append(top, title, detail);
      if (record.assessment_id !== null && record.assessment_id !== undefined && String(record.assessment_id).trim()) {
        const link = document.createElement('a'); link.className = 'record-link'; link.href = `vet-summary.html?animal_id=${encodeURIComponent(animalId)}&assessment_id=${encodeURIComponent(record.assessment_id)}`; link.textContent = t('viewSummary'); article.appendChild(link);
      }
      el.summaries.appendChild(article);
    });
  }

  function renderPassport() {
    if (!passport) return;
    const animal = passport.animal;
    const assessments = Array.isArray(passport.assessments) ? passport.assessments : [];
    const summaries = Array.isArray(passport.vet_case_summaries) ? passport.vet_case_summaries : [];
    const reminders = passport.reminders && typeof passport.reminders === 'object' ? passport.reminders : {};
    renderAnimal(animal);
    renderOverview(assessments);
    renderAssessments(assessments);
    renderReminderList(el.upcoming, el.upcomingEmpty, Array.isArray(reminders.upcoming) ? reminders.upcoming : [], 1);
    renderReminderList(el.past, el.pastEmpty, Array.isArray(reminders.past) ? reminders.past : [], -1);
    renderSummaries(summaries);
  }

  function showError(kind) {
    errorKind = kind;
    el.loading.classList.add('hidden'); el.page.classList.add('hidden'); el.error.classList.remove('hidden');
    el.errorTitle.textContent = t(`${kind}Title`);
    el.errorMessage.textContent = t(`${kind}Message`);
    el.retry.classList.toggle('hidden', kind === 'missing' || kind === 'notFound');
  }

  async function loadPassport() {
    errorKind = null; passport = null;
    el.error.classList.add('hidden'); el.page.classList.add('hidden'); el.loading.classList.remove('hidden');
    if (!animalId || !animalId.trim()) { showError('missing'); return; }
    try {
      const data = await window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(animalId)}/passport`, { headers: { Accept: 'application/json' } });
      if (!data || typeof data !== 'object' || !data.animal || typeof data.animal !== 'object') { showError('malformed'); return; }
      passport = data;
      renderPassport();
      el.loading.classList.add('hidden'); el.page.classList.remove('hidden');
    } catch (error) {
      console.error('Health Passport could not be loaded.', error);
      showError(error.status === 404 ? 'notFound' : error.status === 403 ? 'forbidden' : 'connection');
    }
  }

  function applyLanguage(nextLanguage) {
    language = window.MaweshiI18n.applyPage(nextLanguage, copy).language;
    if (passport) renderPassport();
    if (errorKind) showError(errorKind);
  }

  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) applyLanguage(languageButton.dataset.language);
  });
  el.retry.addEventListener('click', loadPassport);

  setLinks();
  applyLanguage(language);
  loadPassport();
})();
