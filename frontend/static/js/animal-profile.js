(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
  const animalId = new URLSearchParams(window.location.search).get('id');

  const copy = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں',
      backToAnimals: 'جانوروں کی فہرست پر واپس جائیں', backToAnimalsShort: 'جانوروں کی فہرست', loadingLabel: 'جانور کا ریکارڈ لوڈ ہو رہا ہے',
      tryAgain: 'دوبارہ کوشش کریں', logout: 'لاگ آؤٹ', editAnimal: 'جانور کی معلومات بدلیں', profileDetails: 'جانور کی تفصیل', basicInformation: 'بنیادی معلومات',
      animalType: 'جانور کی قسم', breed: 'نسل', gender: 'جنس', age: 'عمر', weight: 'وزن', color: 'رنگ',
      healthStatus: 'موجودہ صحت', recordCreated: 'ریکارڈ بنایا گیا', careNotes: 'دیکھ بھال کی باتیں', notes: 'نوٹس',
      healthRecord: 'صحت کا ریکارڈ', recentActivity: 'حالیہ صحت کی سرگرمی', refresh: 'تازہ کریں', loadingActivity: 'صحت کا ریکارڈ دیکھا جا رہا ہے…',
      noAssessments: 'ابھی تک صحت کا کوئی معائنہ موجود نہیں ہے۔', startFirstAssessment: 'پہلا معائنہ شروع کریں', viewResult: 'نتیجہ دیکھیں',
      activityUnavailable: 'صحت کا ریکارڈ ابھی نہیں دکھایا جا سکتا۔', animalHealth: 'جانور کی صحت', quickActions: 'فوری کام',
      startAssessment: 'صحت کا معائنہ شروع کریں', assessmentHelp: 'تصویر اور علامات کے ساتھ', healthHistory: 'صحت کی پچھلی تفصیل',
      preventiveCare: 'بیماری سے بچاؤ', followUp: 'دوبارہ جانچ', healthPassport: 'صحت پاسپورٹ', comingSoon: 'جلد آرہا ہے',
      recordSettings: 'ریکارڈ کی ترتیب', deleteHelp: 'اگر یہ ریکارڈ مزید نہیں چاہیے تو اسے حذف کر سکتے ہیں۔', deleteAnimal: 'جانور کا ریکارڈ حذف کریں',
      footerCare: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔', footerDisclaimer: 'AI کی رائے ابتدائی رہنمائی ہے، ڈاکٹر کا متبادل نہیں۔',
      editRecord: 'ریکارڈ میں تبدیلی', closeFormLabel: 'فارم بند کریں', name: 'نام', notRecorded: 'درج نہیں', female: 'مادہ', male: 'نر',
      ageYears: 'عمر (سال)', weightKg: 'وزن (کلو)', healthy: 'صحت مند', needsAttention: 'توجہ درکار', underTreatment: 'علاج جاری ہے',
      cancel: 'منسوخ کریں', saveChanges: 'تبدیلی محفوظ کریں', saving: 'محفوظ ہو رہا ہے…', assessmentInstructions: 'جانور کی صاف تصویر اور نظر آنے والی علامات لکھیں۔',
      animalPhoto: 'جانور کی تصویر', uploadImage: 'تصویر اپ لوڈ کریں', takePhoto: 'تصویر لیں', noImageSelected: 'ابھی کوئی تصویر منتخب نہیں ہوئی۔', selectedImage: 'منتخب تصویر: {name}', imageRequired: 'براہِ کرم تصویر اپ لوڈ کریں یا نئی تصویر لیں۔', imageHelp: 'JPG، PNG یا WebP — زیادہ سے زیادہ 5 MB', symptoms: 'علامات',
      symptomsPlaceholder: 'مثلاً جانور کھانا نہیں کھا رہا اور سست ہے', assessmentSafety: 'یہ ابتدائی AI رہنمائی ہے۔ ہنگامی حالت میں فوراً جانوروں کے ڈاکٹر سے رابطہ کریں۔',
      beginAssessment: 'معائنہ کریں', assessing: 'معائنہ ہو رہا ہے…', deleteQuestion: 'کیا یہ جانور حذف کرنا ہے؟',
      deleteWarning: 'اس جانور کا ریکارڈ ختم ہو جائے گا۔ یہ عمل واپس نہیں ہو سکتا۔', keepAnimal: 'ریکارڈ رہنے دیں', confirmDelete: 'ہاں، حذف کریں', deleting: 'حذف ہو رہا ہے…',
      pageNotFound: 'جانور کا ریکارڈ نہیں ملا', notFoundMessage: 'یہ ریکارڈ موجود نہیں یا حذف ہو چکا ہے۔', forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ ریکارڈ دیکھنے کی اجازت نہیں ہے۔', connectionTitle: 'ریکارڈ ابھی دستیاب نہیں',
      connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔', recordNumber: 'ریکارڈ', updatedOn: 'آخری تبدیلی',
      noNotes: 'کوئی نوٹ درج نہیں کیا گیا۔', year: 'سال', kg: 'کلو', recordUpdated: 'جانور کی معلومات محفوظ ہو گئیں۔',
      assessmentSaved: 'صحت کا معائنہ ریکارڈ ہو گیا۔', couldNotSave: 'معلومات محفوظ نہیں ہو سکیں۔ دوبارہ کوشش کریں۔',
      couldNotAssess: 'معائنہ مکمل نہیں ہو سکا۔ دوبارہ کوشش کریں۔', couldNotDelete: 'ریکارڈ حذف نہیں ہو سکا۔ دوبارہ کوشش کریں۔',
      imageTooLarge: 'تصویر 5 MB سے کم ہونی چاہیے۔', imageBlurry: 'تصویر دھندلی ہے۔ براہِ کرم صاف تصویر منتخب کر کے دوبارہ کوشش کریں۔', imageDark: 'تصویر بہت تاریک ہے۔ براہِ کرم بہتر روشنی میں تصویر لے کر دوبارہ کوشش کریں۔', imageLowResolution: 'تصویر کی کوالٹی بہت کم ہے۔ براہِ کرم زیادہ واضح تصویر منتخب کر کے دوبارہ کوشش کریں۔', imageUnreadable: 'تصویر پڑھی نہیں جا سکی۔ براہِ کرم دوسری JPG، PNG یا WebP تصویر منتخب کریں۔', imageInvalidType: 'تصویر کا فارمیٹ درست نہیں۔ براہِ کرم JPG، PNG یا WebP تصویر منتخب کریں۔',
      statusPending: 'جاری ہے', statusCompleted: 'مکمل', statusFailed: 'مکمل نہیں ہوا',
      urgencyLow: 'معمولی توجہ', urgencyMedium: 'توجہ درکار', urgencyHigh: 'فوری توجہ', noConditionSummary: 'کوئی بیماری درج نہیں',
      preliminaryResult: 'ابتدائی نتیجہ', assessmentDate: 'معائنے کی تاریخ'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language',
      backToAnimals: 'Back to animals', backToAnimalsShort: 'Animal dashboard', loadingLabel: 'Loading animal record', tryAgain: 'Try again', logout: 'Logout',
      editAnimal: 'Edit animal', profileDetails: 'Animal details', basicInformation: 'Basic information', animalType: 'Animal type', breed: 'Breed',
      gender: 'Gender', age: 'Age', weight: 'Weight', color: 'Color', healthStatus: 'Current health status', recordCreated: 'Record created',
      careNotes: 'Care notes', notes: 'Notes', healthRecord: 'Health record', recentActivity: 'Recent health activity', refresh: 'Refresh',
      loadingActivity: 'Loading health activity…', noAssessments: 'No health assessments yet.', startFirstAssessment: 'Start the first assessment', viewResult: 'View Result',
      activityUnavailable: 'Health activity cannot be shown right now.', animalHealth: 'Animal health', quickActions: 'Quick actions',
      startAssessment: 'Start Health Assessment', assessmentHelp: 'With a photo and symptoms', healthHistory: 'Health History', preventiveCare: 'Preventive Care',
      followUp: 'Follow-Up', healthPassport: 'Health Passport', comingSoon: 'Coming soon', recordSettings: 'Record settings',
      deleteHelp: 'If this record is no longer needed, you can remove it.', deleteAnimal: 'Delete animal record',
      footerCare: 'Built to support better livestock care.', footerDisclaimer: 'AI guidance is preliminary and does not replace a veterinarian.',
      editRecord: 'Edit record', closeFormLabel: 'Close form', name: 'Name', notRecorded: 'Not recorded', female: 'Female', male: 'Male',
      ageYears: 'Age in years', weightKg: 'Weight in kg', healthy: 'Healthy', needsAttention: 'Needs attention', underTreatment: 'Under treatment',
      cancel: 'Cancel', saveChanges: 'Save changes', saving: 'Saving…', assessmentInstructions: 'Add a clear photo and describe the symptoms you can see.',
      animalPhoto: 'Animal photo', uploadImage: 'Upload image', takePhoto: 'Take photo', noImageSelected: 'No image selected yet.', selectedImage: 'Selected image: {name}', imageRequired: 'Please upload an image or take a new photo.', imageHelp: 'JPG, PNG or WebP — maximum 5 MB', symptoms: 'Symptoms',
      symptomsPlaceholder: 'e.g. The animal is not eating and seems tired', assessmentSafety: 'This is preliminary AI guidance. Contact a veterinarian immediately in an emergency.',
      beginAssessment: 'Begin assessment', assessing: 'Assessing…', deleteQuestion: 'Delete this animal?',
      deleteWarning: 'This will remove this animal record. This action cannot be undone.', keepAnimal: 'Keep animal', confirmDelete: 'Yes, delete', deleting: 'Deleting…',
      pageNotFound: 'Animal record not found', notFoundMessage: 'This record does not exist or may have been removed.', forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to access this record.', connectionTitle: 'Record unavailable right now',
      connectionMessage: 'We could not connect. Please try again in a little while.', recordNumber: 'Record', updatedOn: 'Last updated',
      noNotes: 'No notes recorded.', year: 'yr', kg: 'kg', recordUpdated: 'Animal information was saved.',
      assessmentSaved: 'The health assessment was recorded.', couldNotSave: 'The information could not be saved. Please try again.',
      couldNotAssess: 'The assessment could not be completed. Please try again.', couldNotDelete: 'The record could not be deleted. Please try again.',
      imageTooLarge: 'The image must be smaller than 5 MB. Please choose another image and try again.', imageBlurry: 'Image is too blurry to analyze. Please upload a clearer photo.', imageDark: 'Image is too dark. Please choose a brighter photo and try again.', imageLowResolution: 'Image resolution is too low. Please choose a clearer, higher-resolution photo and try again.', imageUnreadable: 'Image could not be processed. Please choose another JPG, PNG or WebP image.', imageInvalidType: 'This image format is not accepted. Please choose a JPG, PNG or WebP image.',
      statusPending: 'Pending', statusCompleted: 'Completed', statusFailed: 'Not completed',
      urgencyLow: 'Low urgency', urgencyMedium: 'Needs attention', urgencyHigh: 'Urgent attention', noConditionSummary: 'No condition recorded',
      preliminaryResult: 'Preliminary result', assessmentDate: 'Assessment date'
    }
  };

  const el = {
    loading: document.querySelector('#profile-loading'), error: document.querySelector('#profile-error'), content: document.querySelector('#profile-content'),
    errorTitle: document.querySelector('#profile-error-title'), errorMessage: document.querySelector('#profile-error-message'), feedback: document.querySelector('#page-feedback'),
    name: document.querySelector('#animal-name'), kind: document.querySelector('#animal-kind'), typeIcon: document.querySelector('#animal-type-icon'),
    healthBadge: document.querySelector('#animal-health-badge'), idLabel: document.querySelector('#animal-id-label'), updated: document.querySelector('#updated-date'),
    infoType: document.querySelector('#info-type'), infoBreed: document.querySelector('#info-breed'), infoGender: document.querySelector('#info-gender'),
    infoAge: document.querySelector('#info-age'), infoWeight: document.querySelector('#info-weight'), infoColor: document.querySelector('#info-color'),
    infoHealth: document.querySelector('#info-health'), created: document.querySelector('#created-date'), notes: document.querySelector('#animal-notes'),
    activityLoading: document.querySelector('#activity-loading'), activityList: document.querySelector('#activity-list'), activityEmpty: document.querySelector('#activity-empty'),
    activityError: document.querySelector('#activity-error'), editDialog: document.querySelector('#edit-dialog'), editForm: document.querySelector('#edit-form'),
    editAlert: document.querySelector('#edit-alert'), saveEdit: document.querySelector('#save-edit'), assessmentDialog: document.querySelector('#assessment-dialog'),
    assessmentForm: document.querySelector('#assessment-form'), assessmentAlert: document.querySelector('#assessment-alert'), submitAssessment: document.querySelector('#submit-assessment'),
    uploadInput: document.querySelector('#assessment-upload-input'), cameraInput: document.querySelector('#assessment-camera-input'), imageSelection: document.querySelector('#assessment-image-selection'),
    deleteDialog: document.querySelector('#delete-dialog'), deleteAlert: document.querySelector('#delete-alert'), confirmDelete: document.querySelector('#confirm-delete'),
    historyLink: document.querySelector('#health-history-link'), preventiveLink: document.querySelector('#preventive-care-link')
  };

  let language = window.MaweshiI18n.getLanguage();
  let animal = null;
  let assessments = [];
  let pageErrorKind = null;

  class RequestError extends Error {
    constructor(message, status, details) { super(message); this.status = status; this.details = details; }
  }

  function t(key) { return copy[language][key] || key; }

  const api = {
    getAnimal: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, { headers: { Accept: 'application/json' } }),
    getAssessments: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/assessments`, { headers: { Accept: 'application/json' } }),
    updateAnimal: (id, payload) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload)
    }),
    deleteAnimal: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, { method: 'DELETE', headers: { Accept: 'application/json' } }),
    createAssessment: (id, formData) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/assessments`, { method: 'POST', body: formData })
  };

  function translatePage() {
    language = window.MaweshiI18n.applyPage(language, copy).language;
    if (animal) renderAnimal();
    if (assessments.length) renderAssessments();
    if (pageErrorKind !== null) showPageError(pageErrorKind);
    updateImageSelection();
  }

  function value(raw, fallback = t('notRecorded')) { return raw === null || raw === undefined || String(raw).trim() === '' ? fallback : String(raw); }
  function translatedValue(raw) {
    return { Female: t('female'), Male: t('male'), Healthy: t('healthy'), 'Needs attention': t('needsAttention'), 'Under treatment': t('underTreatment') }[raw] || value(raw);
  }
  function normalStatus(raw) { return value(raw).trim().toLowerCase(); }
  function statusClass(raw) {
    const status = normalStatus(raw);
    if (['healthy', 'good', 'fit'].includes(status)) return 'health-badge--healthy';
    if (status.includes('attention') || status.includes('treatment') || status.includes('sick') || status.includes('critical')) return 'health-badge--attention';
    return 'health-badge--unknown';
  }
  function animalIcon(type) {
    const normalized = value(type, '').toLowerCase();
    if (normalized.includes('buffalo') || normalized.includes('بھینس')) return '🐃';
    if (normalized.includes('goat') || normalized.includes('بکری') || normalized.includes('بکرا')) return '🐐';
    if (normalized.includes('sheep') || normalized.includes('بھیڑ') || normalized.includes('دنبہ')) return '🐑';
    if (normalized.includes('cow') || normalized.includes('cattle') || normalized.includes('گائے') || normalized.includes('بیل')) return '🐄';
    return '🐾';
  }
  function formatDate(raw, includeTime = false) {
    if (!raw) return t('notRecorded');
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) return t('notRecorded');
    const options = { day: 'numeric', month: 'short', year: 'numeric' };
    if (includeTime) Object.assign(options, { hour: 'numeric', minute: '2-digit' });
    return new Intl.DateTimeFormat(language === 'ur' ? 'ur-PK' : 'en-PK', options).format(date);
  }

  function renderAnimal() {
    el.name.textContent = value(animal.name);
    el.kind.textContent = [value(animal.animal_type, ''), value(animal.breed, '')].filter(Boolean).join(' · ') || t('notRecorded');
    el.typeIcon.textContent = animalIcon(animal.animal_type);
    el.healthBadge.className = `health-badge ${statusClass(animal.health_status)}`;
    el.healthBadge.textContent = translatedValue(animal.health_status);
    el.idLabel.textContent = `${t('recordNumber')} #${String(animal.id).slice(-6)}`;
    el.updated.textContent = `${t('updatedOn')}: ${formatDate(animal.updated_at)}`;
    el.infoType.textContent = value(animal.animal_type);
    el.infoBreed.textContent = value(animal.breed);
    el.infoGender.textContent = translatedValue(animal.gender);
    el.infoAge.textContent = animal.age === null || animal.age === undefined ? t('notRecorded') : `${animal.age} ${t('year')}`;
    el.infoWeight.textContent = animal.weight === null || animal.weight === undefined ? t('notRecorded') : `${animal.weight} ${t('kg')}`;
    el.infoColor.textContent = value(animal.color);
    el.infoHealth.textContent = translatedValue(animal.health_status);
    el.created.textContent = formatDate(animal.created_at);
    el.notes.textContent = animal.notes && String(animal.notes).trim() ? animal.notes : t('noNotes');
    document.title = `${value(animal.name)} | Maweshi Muhafiz`;
  }

  function clearActivityStates() {
    [el.activityLoading, el.activityList, el.activityEmpty, el.activityError].forEach((node) => node.classList.add('hidden'));
  }
  function activityStatus(record) { return t(record.status === 'completed' ? 'statusCompleted' : record.status === 'failed' ? 'statusFailed' : 'statusPending'); }
  function urgencyCopy(level) { return t(level === 'high' ? 'urgencyHigh' : level === 'low' ? 'urgencyLow' : 'urgencyMedium'); }

  function renderAssessments() {
    clearActivityStates();
    if (!assessments.length) { el.activityEmpty.classList.remove('hidden'); return; }
    const sorted = [...assessments].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)).slice(0, 3);
    const fragment = document.createDocumentFragment();
    sorted.forEach((record) => {
      const result = record.diagnosis_result && typeof record.diagnosis_result === 'object' ? record.diagnosis_result : null;
      const conditions = result && Array.isArray(result.possible_conditions) ? result.possible_conditions.filter(Boolean).slice(0, 2).join('، ') : '';
      const article = document.createElement('article');
      article.className = 'activity-item';
      const top = document.createElement('div'); top.className = 'activity-item-top';
      const date = document.createElement('time'); date.dateTime = record.created_at || ''; date.textContent = formatDate(record.created_at, true);
      const status = document.createElement('span'); status.className = `assessment-status assessment-status--${record.status || 'pending'}`; status.textContent = activityStatus(record);
      top.append(date, status);
      const heading = document.createElement('h3'); heading.textContent = conditions || t('noConditionSummary');
      const symptoms = document.createElement('p'); symptoms.textContent = value(record.symptoms);
      article.append(top, heading, symptoms);
      if (result && result.urgency_level) {
        const urgency = document.createElement('span'); urgency.className = `urgency-label urgency-label--${result.urgency_level}`; urgency.textContent = urgencyCopy(result.urgency_level);
        article.appendChild(urgency);
      }
      if (record.id !== null && record.id !== undefined && String(record.id).trim() !== '') {
        const viewResult = document.createElement('a');
        viewResult.className = 'profile-action';
        viewResult.href = `assessment-result.html?id=${encodeURIComponent(record.id)}`;
        viewResult.textContent = t('viewResult');
        article.appendChild(viewResult);
      }
      fragment.appendChild(article);
    });
    el.activityList.replaceChildren(fragment);
    el.activityList.classList.remove('hidden');
  }

  function showPageError(kind) {
    pageErrorKind = kind;
    el.loading.classList.add('hidden'); el.content.classList.add('hidden'); el.error.classList.remove('hidden');
    el.errorTitle.textContent = t(kind === 'notFound' ? 'pageNotFound' : kind === 'forbidden' ? 'forbiddenTitle' : 'connectionTitle');
    el.errorMessage.textContent = t(kind === 'notFound' ? 'notFoundMessage' : kind === 'forbidden' ? 'forbiddenMessage' : 'connectionMessage');
  }
  function showFeedback(message) {
    el.feedback.textContent = message; el.feedback.classList.remove('hidden');
    window.clearTimeout(showFeedback.timer); showFeedback.timer = window.setTimeout(() => el.feedback.classList.add('hidden'), 4500);
  }

  async function loadProfile() {
    pageErrorKind = null;
    el.error.classList.add('hidden'); el.content.classList.add('hidden'); el.loading.classList.remove('hidden');
    if (!animalId) { showPageError('notFound'); return; }
    try {
      animal = await api.getAnimal(animalId);
      renderAnimal();
      el.loading.classList.add('hidden'); el.content.classList.remove('hidden');
      loadAssessments();
    } catch (error) {
      console.error(error);
      showPageError(error.status === 404 ? 'notFound' : error.status === 403 ? 'forbidden' : 'connection');
    }
  }

  async function loadAssessments() {
    clearActivityStates(); el.activityLoading.classList.remove('hidden');
    try {
      const data = await api.getAssessments(animalId);
      assessments = Array.isArray(data) ? data : [];
      renderAssessments();
    } catch (error) {
      console.error(error); clearActivityStates(); el.activityError.classList.remove('hidden');
    }
  }

  function setFormValue(form, field, raw) {
    const control = form.elements[field];
    const normalized = raw === null || raw === undefined ? '' : String(raw);
    if (control.tagName === 'SELECT' && normalized && !Array.from(control.options).some((option) => option.value === normalized)) {
      const option = new Option(normalized, normalized);
      option.dataset.dynamic = 'true';
      control.add(option);
    }
    control.value = normalized;
  }
  function openEdit() {
    el.editForm.querySelectorAll('option[data-dynamic]').forEach((option) => option.remove());
    ['name', 'animal_type', 'breed', 'gender', 'age', 'weight', 'color', 'health_status', 'notes'].forEach((field) => setFormValue(el.editForm, field, animal[field]));
    el.editAlert.classList.add('hidden'); el.editDialog.showModal();
  }
  function optional(formData, key) { const raw = String(formData.get(key) || '').trim(); return raw || null; }
  function editPayload() {
    const data = new FormData(el.editForm);
    const payload = { name: String(data.get('name') || '').trim(), animal_type: String(data.get('animal_type') || '').trim() };
    ['breed', 'gender', 'color', 'health_status', 'notes'].forEach((key) => { payload[key] = optional(data, key); });
    ['age', 'weight'].forEach((key) => { const raw = String(data.get(key) || '').trim(); payload[key] = raw === '' ? null : Number(raw); });
    return payload;
  }

  async function submitEdit(event) {
    event.preventDefault(); el.editAlert.classList.add('hidden');
    if (!el.editForm.reportValidity()) return;
    el.saveEdit.disabled = true; el.saveEdit.textContent = t('saving');
    try {
      animal = await api.updateAnimal(animalId, editPayload());
      renderAnimal(); el.editDialog.close(); showFeedback(t('recordUpdated'));
    } catch (error) {
      console.error(error); el.editAlert.textContent = t('couldNotSave'); el.editAlert.classList.remove('hidden');
    } finally { el.saveEdit.disabled = false; el.saveEdit.textContent = t('saveChanges'); }
  }

  function selectedAssessmentImage() {
    return el.cameraInput.files?.[0] || el.uploadInput.files?.[0] || null;
  }

  function updateImageSelection() {
    const image = selectedAssessmentImage();
    el.imageSelection.textContent = image ? t('selectedImage').replace('{name}', image.name) : t('noImageSelected');
    el.imageSelection.dir = image ? 'auto' : '';
  }

  function useSelectedImage(source, other) {
    if (source.files?.length) other.value = '';
    updateImageSelection();
  }

  function openAssessment() { el.assessmentAlert.classList.add('hidden'); updateImageSelection(); el.assessmentDialog.showModal(); }

  function assessmentImageErrorMessage(error) {
    if (error?.status !== 400) return '';
    const backendErrors = Array.isArray(error?.payload?.error)
      ? error.payload.error
      : [error?.payload?.error, error?.payload?.message, error?.message, error?.details];
    const messages = [];

    backendErrors.filter((item) => typeof item === 'string').forEach((item) => {
      const message = item.trim();
      if (!message) return;
      if (message === 'Image is too blurry to analyze. Please upload a clearer photo.') messages.push(t('imageBlurry'));
      else if (message === 'Image is too dark') messages.push(t('imageDark'));
      else if (message === 'Image resolution is too low') messages.push(t('imageLowResolution'));
      else if (message === 'Image could not be processed') messages.push(t('imageUnreadable'));
      else if (message.startsWith('Content type ') && message.includes(' is not allowed.')) messages.push(t('imageInvalidType'));
      else if (message.startsWith('File size (') && message.includes('exceeds the maximum allowed size')) messages.push(t('imageTooLarge'));
    });

    return [...new Set(messages)].join(' ');
  }

  async function submitAssessment(event) {
    event.preventDefault(); el.assessmentAlert.classList.add('hidden');
    if (!el.assessmentForm.reportValidity()) return;
    const image = selectedAssessmentImage();
    if (!image) { el.assessmentAlert.textContent = t('imageRequired'); el.assessmentAlert.classList.remove('hidden'); return; }
    const data = new FormData(el.assessmentForm);
    data.set('image', image, image.name || 'animal-photo.jpg');
    if (image.size > MAX_IMAGE_BYTES) { el.assessmentAlert.textContent = t('imageTooLarge'); el.assessmentAlert.classList.remove('hidden'); return; }
    el.submitAssessment.disabled = true; el.submitAssessment.textContent = t('assessing');
    try {
      const assessment = await api.createAssessment(animalId, data);
      if (!assessment || assessment.id === null || assessment.id === undefined || String(assessment.id).trim() === '') {
        throw new RequestError('Assessment id missing', 200);
      }
      el.assessmentForm.reset();
      el.uploadInput.value = '';
      el.cameraInput.value = '';
      updateImageSelection();
      window.location.assign(`assessment-result.html?id=${encodeURIComponent(assessment.id)}`);
    } catch (error) {
      console.error(error);
      el.assessmentAlert.textContent = assessmentImageErrorMessage(error) || t('couldNotAssess');
      el.assessmentAlert.classList.remove('hidden');
    } finally { el.submitAssessment.disabled = false; el.submitAssessment.textContent = t('beginAssessment'); }
  }

  async function deleteAnimal() {
    el.deleteAlert.classList.add('hidden'); el.confirmDelete.disabled = true; el.confirmDelete.textContent = t('deleting');
    try { await api.deleteAnimal(animalId); window.location.assign('index.html'); }
    catch (error) {
      console.error(error); el.deleteAlert.textContent = t('couldNotDelete'); el.deleteAlert.classList.remove('hidden');
      el.confirmDelete.disabled = false; el.confirmDelete.textContent = t('confirmDelete');
    }
  }

  function closeDialog(button) { const dialog = button.closest('dialog'); if (dialog) dialog.close(); }
  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) { language = window.MaweshiI18n.setLanguage(languageButton.dataset.language); translatePage(); }
    if (event.target.closest('[data-open-edit]')) openEdit();
    if (event.target.closest('[data-open-assessment]')) openAssessment();
    if (event.target.closest('[data-choose-upload]')) el.uploadInput.click();
    if (event.target.closest('[data-take-photo]')) el.cameraInput.click();
    if (event.target.closest('[data-open-delete]')) { el.deleteAlert.classList.add('hidden'); el.deleteDialog.showModal(); }
    if (event.target.closest('[data-close-dialog]')) closeDialog(event.target.closest('[data-close-dialog]'));
    if (event.target.closest('[data-retry-activity]')) loadAssessments();
  });
  document.querySelectorAll('dialog').forEach((dialog) => dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); }));
  document.querySelector('#retry-profile').addEventListener('click', loadProfile);
  document.querySelector('#refresh-activity').addEventListener('click', loadAssessments);
  el.editForm.addEventListener('submit', submitEdit);
  el.assessmentForm.addEventListener('submit', submitAssessment);
  el.uploadInput.addEventListener('change', () => useSelectedImage(el.uploadInput, el.cameraInput));
  el.cameraInput.addEventListener('change', () => useSelectedImage(el.cameraInput, el.uploadInput));
  el.confirmDelete.addEventListener('click', deleteAnimal);

  el.historyLink.href = animalId ? `health-history.html?id=${encodeURIComponent(animalId)}` : 'index.html';
  el.preventiveLink.href = animalId ? `preventive-care.html?id=${encodeURIComponent(animalId)}` : 'index.html';
  translatePage();
  loadProfile();
})();
