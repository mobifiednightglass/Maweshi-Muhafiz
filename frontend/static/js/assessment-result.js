(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const assessmentId = new URLSearchParams(window.location.search).get('id');

  const copy = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں', logout: 'لاگ آؤٹ', backToProfile: 'جانور کے پروفائل پر واپس جائیں',
      healthAssessment: 'صحت کا معائنہ', pageTitle: 'صحت کے معائنے کا نتیجہ', loadingLabel: 'نتیجہ دیکھا جا رہا ہے', tryAgain: 'دوبارہ کوشش کریں',
      missingTitle: 'معائنے کا ریکارڈ نہیں ملا', missingMessage: 'نتیجہ دیکھنے کے لیے درست معائنہ منتخب کریں۔', notFoundTitle: 'معائنے کا ریکارڈ نہیں ملا',
      notFoundMessage: 'یہ معائنہ موجود نہیں یا دستیاب نہیں رہا۔', connectionTitle: 'نتیجہ ابھی دستیاب نہیں', connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔',
      malformedTitle: 'نتیجے کی مکمل تفصیل دستیاب نہیں', malformedMessage: 'یہ معائنہ محفوظ ہے، لیکن اس کی مکمل تفصیل ابھی نہیں دکھائی جا سکتی۔', forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ ریکارڈ دیکھنے کی اجازت نہیں ہے۔',
      processingLabel: 'جائزہ جاری ہے', pendingTitle: 'صحت کا معائنہ مکمل ہو رہا ہے', pendingMessage: 'نتیجہ ابھی تیار نہیں۔ کچھ دیر بعد صحت کی پچھلی تفصیل سے دوبارہ دیکھیں۔',
      notCompletedLabel: 'معائنہ مکمل نہیں ہوا', failedTitle: 'ہم یہ صحت کا معائنہ مکمل نہیں کر سکے', failedMessage: 'براہِ کرم دوبارہ کوشش کریں۔ صاف تصویر اور واضح علامات بہتر مدد دے سکتی ہیں۔',
      tryAssessmentAgain: 'دوبارہ معائنہ کریں', preliminaryFindings: 'ابتدائی معلومات', possibleConditions: 'ممکنہ بیماریاں',
      conditionsHelp: 'یہ AI کی مدد سے بتائی گئی ممکنہ حالتیں ہیں، حتمی تشخیص نہیں۔', noConditions: 'کوئی ممکنہ بیماری نہیں بتائی گئی۔',
      assessmentDetails: 'معائنے کی تفصیل', explanation: 'وضاحت', aiConfidence: 'AI کی یقین دہانی', keepInMind: 'یہ بات ذہن میں رکھیں',
      practicalGuidance: 'عملی رہنمائی', safeNextSteps: 'محفوظ اگلے قدم', safeNextStepsHelp: 'یہ احتیاطی قدم معائنے کی فوری توجہ کے مطابق دیے گئے ہیں۔',
      listenInUrdu: 'اردو میں سنیں', loadingSpeech: 'آواز تیار ہو رہی ہے…', playingSpeech: 'آواز چل رہی ہے…', replayInUrdu: 'دوبارہ اردو میں سنیں', speechUnavailable: 'آواز ابھی نہیں چل سکی۔ دوبارہ کوشش کریں۔',
      farmerReport: 'کسان کی بتائی ہوئی معلومات', reportedSymptoms: 'بتائی گئی علامات', noSymptoms: 'کوئی علامات درج نہیں کی گئیں۔',
      safetyLabel: 'اہم حفاظتی بات', safetyMessage: 'مویشی محافظ AI کی مدد سے ابتدائی صحت جانچ اور ممکنہ بیماریوں کی معلومات دیتا ہے۔ یہ جانوروں کے مستند ڈاکٹر کا متبادل نہیں۔',
      redFlagLabel: 'ہنگامی علامت', redFlagTitle: 'فوری جانوروں کے ڈاکٹر سے رابطہ کریں', redFlagMessage: 'اس معائنے میں ہنگامی توجہ کی علامت سامنے آئی ہے۔', redFlagReasons: 'سامنے آنے والی علامات',
      vetReadySummary: 'ڈاکٹر کے لیے خلاصہ', viewHealthHistory: 'صحت کی پچھلی تفصیل دیکھیں', footerCare: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔',
      footerDisclaimer: 'AI کی رائے ابتدائی رہنمائی ہے، ڈاکٹر کا متبادل نہیں۔', assessmentDate: 'معائنے کی تاریخ', animalRecord: 'جانور کا ریکارڈ',
      urgencyLowLabel: 'کم فوری توجہ', urgencyLowTitle: 'فوری توجہ کی ضرورت کم ہے', urgencyLowMessage: 'اس معائنے میں فوری توجہ کی سطح کم بتائی گئی ہے۔ نیچے ممکنہ حالتیں اور غیر یقینی باتیں دیکھیں۔',
      urgencyMediumLabel: 'توجہ درکار', urgencyMediumTitle: 'اس جانور کو توجہ کی ضرورت ہے', urgencyMediumMessage: 'اس معائنے میں ایسی علامات ظاہر ہوئی ہیں جن پر توجہ درکار ہے۔ نیچے ممکنہ حالتیں اور غیر یقینی باتیں دیکھیں۔',
      urgencyHighLabel: 'فوری توجہ', urgencyHighTitle: 'جانوروں کے ڈاکٹر سے جلد رابطہ کریں', urgencyHighMessage: 'معائنے میں زیادہ فوری توجہ کی ضرورت ظاہر ہوئی ہے۔ پیشہ ورانہ مدد میں تاخیر نہ کریں۔'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language', logout: 'Logout', backToProfile: 'Back to Animal Profile',
      healthAssessment: 'Health assessment', pageTitle: 'Health Assessment Result', loadingLabel: 'Loading assessment result', tryAgain: 'Try again',
      missingTitle: 'Assessment record not found', missingMessage: 'Select a valid assessment to view its result.', notFoundTitle: 'Assessment record not found',
      notFoundMessage: 'This assessment does not exist or is no longer available.', connectionTitle: 'Result unavailable right now', connectionMessage: 'We could not connect. Please try again in a little while.',
      malformedTitle: 'Complete result details are unavailable', malformedMessage: 'This assessment is saved, but its complete details cannot be shown right now.', forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to access this record.',
      processingLabel: 'Processing', pendingTitle: 'Health assessment is being completed', pendingMessage: 'The result is not ready yet. Please check it again later from Health History.',
      notCompletedLabel: 'Assessment not completed', failedTitle: "We couldn't complete this health assessment", failedMessage: 'Please try again. A clear photo and clearly described symptoms may help.',
      tryAssessmentAgain: 'Try assessment again', preliminaryFindings: 'Preliminary findings', possibleConditions: 'Possible Conditions',
      conditionsHelp: 'These are AI-suggested possible conditions, not a confirmed diagnosis.', noConditions: 'No possible conditions were returned.',
      assessmentDetails: 'Assessment details', explanation: 'Explanation', aiConfidence: 'AI confidence', keepInMind: 'What to keep in mind',
      practicalGuidance: 'Practical guidance', safeNextSteps: 'Safe Next Steps', safeNextStepsHelp: 'These precautionary steps are provided according to the assessment urgency.',
      listenInUrdu: 'Listen in Urdu', loadingSpeech: 'Preparing audio…', playingSpeech: 'Playing audio…', replayInUrdu: 'Listen again in Urdu', speechUnavailable: 'Audio is unavailable right now. Please try again.',
      farmerReport: 'Farmer report', reportedSymptoms: 'Reported Symptoms', noSymptoms: 'No symptoms were recorded.',
      safetyLabel: 'Important safety information', safetyMessage: 'MaweshiMuhafiz provides AI-assisted early health screening and possible conditions. It does not replace a qualified veterinarian.',
      redFlagLabel: 'Emergency warning', redFlagTitle: 'Contact a veterinarian immediately', redFlagMessage: 'This assessment contains a genuine red-flag warning that needs urgent attention.', redFlagReasons: 'Reasons recorded',
      vetReadySummary: 'Vet-Ready Summary', viewHealthHistory: 'View Health History', footerCare: 'Built to support better livestock care.',
      footerDisclaimer: 'AI guidance is preliminary and does not replace a veterinarian.', assessmentDate: 'Assessment date', animalRecord: 'Animal record',
      urgencyLowLabel: 'Low urgency', urgencyLowTitle: 'Lower urgency indicated', urgencyLowMessage: 'This assessment indicates a lower urgency level. Review the possible conditions and uncertainty below.',
      urgencyMediumLabel: 'Needs attention', urgencyMediumTitle: 'This animal needs attention', urgencyMediumMessage: 'This assessment indicates signs that need attention. Review the possible conditions and uncertainty below.',
      urgencyHighLabel: 'Urgent attention', urgencyHighTitle: 'Contact a veterinarian promptly', urgencyHighMessage: 'This assessment indicates that more urgent attention may be required. Do not delay professional help.'
    }
  };

  const el = {
    loading: document.querySelector('#result-loading'), error: document.querySelector('#result-error'), pending: document.querySelector('#result-pending'), failed: document.querySelector('#result-failed'),
    content: document.querySelector('#result-content'), errorTitle: document.querySelector('#result-error-title'), errorMessage: document.querySelector('#result-error-message'), retry: document.querySelector('#retry-result'),
    meta: document.querySelector('#assessment-meta'), animalSummary: document.querySelector('#animal-summary'), date: document.querySelector('#assessment-date'), urgency: document.querySelector('#urgency-panel'),
    urgencyIcon: document.querySelector('#urgency-icon'), urgencyLabel: document.querySelector('#urgency-label'), urgencyHeading: document.querySelector('#urgency-heading'), urgencyMessage: document.querySelector('#urgency-message'),
    conditions: document.querySelector('#conditions-list'), conditionsEmpty: document.querySelector('#conditions-empty'), explanation: document.querySelector('#explanation-text'), confidence: document.querySelector('#confidence-text'), confidenceSection: document.querySelector('.confidence-section'), symptoms: document.querySelector('#symptoms-text'),
    redFlag: document.querySelector('#red-flag-panel'), redFlagReasonsWrap: document.querySelector('#red-flag-reasons-wrap'), redFlagReasons: document.querySelector('#red-flag-reasons'),
    guidanceSection: document.querySelector('#safe-guidance-section'), guidanceList: document.querySelector('#safe-guidance-list'), speechButton: document.querySelector('#listen-urdu-button'), speechStatus: document.querySelector('#speech-status'),
    vetSummaryLink: document.querySelector('#vet-summary-link'), historyLink: document.querySelector('#health-history-link')
  };

  let language = window.MaweshiI18n.getLanguage();
  let assessment = null;
  let animal = null;
  let state = 'loading';
  let errorKind = null;
  let speechAudio = null;
  let speechUrl = '';
  let speechState = 'idle';
  let speechError = false;

  function t(key) { return copy[language][key] || key; }

  const api = {
    getAssessment: (id) => window.MaweshiAuth.request(`${API_BASE}/api/assessments/${encodeURIComponent(id)}`, { headers: { Accept: 'application/json' } }),
    getAnimal: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, { headers: { Accept: 'application/json' } }),
    getSpeech: (animalId, id) => window.MaweshiAuth.requestBlob(`${API_BASE}/api/animals/${encodeURIComponent(animalId)}/assessments/${encodeURIComponent(id)}/speech`, { headers: { Accept: 'audio/wav' } })
  };

  function setProfileLinks(animalId) {
    const destination = animalId === null || animalId === undefined || String(animalId).trim() === '' ? 'index.html' : `animal-profile.html?id=${encodeURIComponent(animalId)}`;
    ['top-profile-link', 'error-profile-link', 'pending-profile-link', 'failed-profile-link', 'retry-assessment-link', 'primary-profile-link'].forEach((id) => {
      document.querySelector(`#${id}`).href = destination;
    });
    const hasIds = animalId !== null && animalId !== undefined && String(animalId).trim() !== '' && assessmentId && assessmentId.trim();
    el.vetSummaryLink.classList.toggle('hidden', !hasIds);
    if (hasIds) el.vetSummaryLink.href = `vet-summary.html?animal_id=${encodeURIComponent(animalId)}&assessment_id=${encodeURIComponent(assessmentId)}`;
    const hasAnimalId = animalId !== null && animalId !== undefined && String(animalId).trim() !== '';
    el.historyLink.classList.toggle('hidden', !hasAnimalId);
    if (hasAnimalId) el.historyLink.href = `health-history.html?id=${encodeURIComponent(animalId)}`;
  }

  function formatDate(raw) {
    if (!raw) return '';
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) return String(raw);
    return new Intl.DateTimeFormat(language === 'ur' ? 'ur-PK' : 'en-PK', { dateStyle: 'medium', timeStyle: 'short' }).format(date);
  }

  function diagnosisIsValid(result) {
    return result && typeof result === 'object' && Array.isArray(result.possible_conditions) &&
      typeof result.explanation === 'string' && typeof result.confidence_note === 'string' &&
      ['low', 'medium', 'high'].includes(result.urgency_level);
  }

  function localizedDiagnosis(result) {
    if (language !== 'ur') {
      return { conditions: result.possible_conditions, explanation: result.explanation, confidence: result.confidence_note, guidance: validStringList(result.safe_next_steps) };
    }
    const urduConditions = Array.isArray(result.possible_conditions_urdu)
      ? result.possible_conditions_urdu.filter((item) => typeof item === 'string' && item.trim())
      : [];
    return {
      conditions: urduConditions.length ? urduConditions : result.possible_conditions,
      explanation: typeof result.explanation_urdu === 'string' && result.explanation_urdu.trim() ? result.explanation_urdu : result.explanation,
      confidence: typeof result.confidence_note_urdu === 'string' && result.confidence_note_urdu.trim() ? result.confidence_note_urdu : result.confidence_note,
      guidance: validStringList(result.safe_next_steps_urdu).length ? validStringList(result.safe_next_steps_urdu) : validStringList(result.safe_next_steps)
    };
  }

  function validStringList(raw) {
    return Array.isArray(raw) ? raw.filter((item) => typeof item === 'string' && item.trim()) : [];
  }

  function updateSpeechControl() {
    const hasUrduSpeech = validStringList(assessment?.diagnosis_result?.safe_next_steps_urdu).length > 0 && Boolean(assessment?.animal_id);
    el.speechButton.classList.toggle('hidden', !hasUrduSpeech);
    if (!hasUrduSpeech) {
      el.speechStatus.textContent = '';
      return;
    }
    el.speechButton.disabled = speechState === 'loading' || speechState === 'playing';
    el.speechButton.textContent = t(speechState === 'loading' ? 'loadingSpeech' : speechState === 'playing' ? 'playingSpeech' : speechState === 'ready' ? 'replayInUrdu' : 'listenInUrdu');
    el.speechStatus.textContent = speechError ? t('speechUnavailable') : '';
    el.speechStatus.classList.toggle('speech-status--error', speechError);
  }

  function renderGuidance(localized) {
    el.guidanceList.replaceChildren();
    localized.guidance.forEach((step) => {
      const item = document.createElement('li');
      item.textContent = step;
      item.dir = 'auto';
      el.guidanceList.appendChild(item);
    });
    el.guidanceSection.classList.toggle('hidden', localized.guidance.length === 0);
    updateSpeechControl();
  }

  function renderRedFlag() {
    const isRedFlag = assessment.is_red_flag === true;
    el.redFlag.classList.toggle('hidden', !isRedFlag);
    el.redFlagReasons.replaceChildren();
    const reasons = Array.isArray(assessment.red_flag_reasons)
      ? assessment.red_flag_reasons.filter((reason) => typeof reason === 'string' && reason.trim())
      : [];
    reasons.forEach((reason) => {
      const item = document.createElement('li');
      item.textContent = reason;
      item.dir = 'auto';
      el.redFlagReasons.appendChild(item);
    });
    el.redFlagReasonsWrap.classList.toggle('hidden', !isRedFlag || reasons.length === 0);
  }

  function clearStates() {
    [el.loading, el.error, el.pending, el.failed, el.content].forEach((node) => node.classList.add('hidden'));
    el.redFlag.classList.add('hidden');
  }

  function urgencyCopy(level) {
    const key = level === 'high' ? 'High' : level === 'low' ? 'Low' : 'Medium';
    return { label: t(`urgency${key}Label`), title: t(`urgency${key}Title`), message: t(`urgency${key}Message`), icon: level === 'low' ? '✓' : '!' };
  }

  function renderHeader() {
    if (!assessment) return;
    el.meta.classList.remove('hidden');
    const hasDate = assessment.created_at !== null && assessment.created_at !== undefined && String(assessment.created_at).trim() !== '';
    el.date.classList.toggle('hidden', !hasDate);
    el.date.textContent = hasDate ? `${t('assessmentDate')}: ${formatDate(assessment.created_at)}` : '';
    el.date.dateTime = hasDate ? assessment.created_at : '';
    if (animal) {
      el.animalSummary.textContent = [animal.name, animal.animal_type].filter((item) => item !== null && item !== undefined && String(item).trim()).join(' · ');
      document.title = `${animal.name || t('pageTitle')} | Maweshi Muhafiz`;
    } else {
      el.animalSummary.textContent = `${t('animalRecord')} #${String(assessment.animal_id || '').slice(-6)}`;
      document.title = `${t('pageTitle')} | Maweshi Muhafiz`;
    }
  }

  function renderCompleted() {
    const result = assessment.diagnosis_result;
    const localized = localizedDiagnosis(result);
    el.confidenceSection.before(el.guidanceSection);
    const urgency = result.urgency_level;
    const urgencyText = urgencyCopy(urgency);
    el.urgency.className = `urgency-panel urgency-panel--${urgency}`;
    el.urgencyIcon.textContent = urgencyText.icon;
    el.urgencyLabel.textContent = urgencyText.label;
    el.urgencyHeading.textContent = urgencyText.title;
    el.urgencyMessage.textContent = urgencyText.message;

    renderRedFlag();
    const conditionItems = localized.conditions.filter((condition) => typeof condition === 'string' && condition.trim());
    el.conditions.replaceChildren();
    conditionItems.forEach((condition) => {
      const item = document.createElement('li');
      item.textContent = condition;
      item.dir = 'auto';
      el.conditions.appendChild(item);
    });
    el.conditions.classList.toggle('hidden', conditionItems.length === 0);
    el.conditionsEmpty.classList.toggle('hidden', conditionItems.length !== 0);
    el.explanation.textContent = localized.explanation;
    renderGuidance(localized);
    el.confidence.textContent = localized.confidence;
    el.symptoms.textContent = typeof assessment.symptoms === 'string' && assessment.symptoms.trim() ? assessment.symptoms : t('noSymptoms');
  }

  async function playUrduGuidance() {
    if (!assessment?.animal_id || !validStringList(assessment?.diagnosis_result?.safe_next_steps_urdu).length) return;
    speechError = false;
    try {
      if (!speechAudio) {
        speechState = 'loading';
        updateSpeechControl();
        const blob = await api.getSpeech(assessment.animal_id, assessmentId);
        if (!blob || blob.size === 0) throw new Error('Empty speech response');
        speechUrl = URL.createObjectURL(blob);
        speechAudio = new Audio(speechUrl);
        speechAudio.addEventListener('ended', () => { speechState = 'ready'; updateSpeechControl(); });
        speechAudio.addEventListener('error', () => { speechState = 'idle'; speechError = true; updateSpeechControl(); });
      } else {
        speechAudio.currentTime = 0;
      }
      speechState = 'playing';
      updateSpeechControl();
      await speechAudio.play();
    } catch (error) {
      console.error('Urdu guidance audio could not be played.', error);
      speechState = 'idle';
      speechError = true;
      updateSpeechControl();
    }
  }

  function render() {
    clearStates();
    renderHeader();
    if (state === 'loading') { el.loading.classList.remove('hidden'); return; }
    if (state === 'error') {
      el.errorTitle.textContent = t(`${errorKind}Title`);
      el.errorMessage.textContent = t(`${errorKind}Message`);
      el.retry.classList.toggle('hidden', errorKind === 'missing');
      el.error.classList.remove('hidden');
      return;
    }
    if (state === 'pending') { renderRedFlag(); el.pending.classList.remove('hidden'); return; }
    if (state === 'failed') {
      renderRedFlag();
      const result = assessment.diagnosis_result && typeof assessment.diagnosis_result === 'object' ? assessment.diagnosis_result : {};
      el.failed.querySelector('.result-state-actions').before(el.guidanceSection);
      renderGuidance(localizedDiagnosis(result));
      el.failed.classList.remove('hidden');
      return;
    }
    renderCompleted();
    el.content.classList.remove('hidden');
  }

  async function loadAnimal() {
    if (!assessment?.animal_id) return;
    try { animal = await api.getAnimal(assessment.animal_id); renderHeader(); }
    catch (error) { console.warn('Animal details could not be loaded for this assessment.', error); }
  }

  async function loadAssessment() {
    if (!assessmentId || !assessmentId.trim()) {
      state = 'error'; errorKind = 'missing'; render(); return;
    }
    state = 'loading'; errorKind = null; render();
    try {
      assessment = await api.getAssessment(assessmentId);
      if (!assessment || typeof assessment !== 'object') { state = 'error'; errorKind = 'malformed'; render(); return; }
      setProfileLinks(assessment.animal_id);
      if (assessment.status === 'pending') state = 'pending';
      else if (assessment.status === 'failed') state = 'failed';
      else if (assessment.status !== 'completed' || !diagnosisIsValid(assessment.diagnosis_result)) { state = 'error'; errorKind = 'malformed'; }
      else state = 'completed';
      render();
      loadAnimal();
    } catch (error) {
      console.error('Assessment result could not be loaded.', error);
      state = 'error'; errorKind = error.status === 404 ? 'notFound' : error.status === 403 ? 'forbidden' : 'connection'; render();
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
  el.retry.addEventListener('click', loadAssessment);
  el.speechButton.addEventListener('click', playUrduGuidance);
  window.addEventListener('beforeunload', () => { if (speechUrl) URL.revokeObjectURL(speechUrl); });

  setProfileLinks(null);
  applyLanguage(language);
  loadAssessment();
})();
