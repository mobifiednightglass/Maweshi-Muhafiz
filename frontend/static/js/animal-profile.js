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
      animalType: 'جانور کی قسم', breed: 'نسل', gender: 'جنس', age: 'عمر', weight: 'وزن', color: 'رنگ', region: 'علاقہ',
      healthStatus: 'موجودہ صحت', recordCreated: 'ریکارڈ بنایا گیا', careNotes: 'دیکھ بھال کی باتیں', notes: 'نوٹس',
      healthRecord: 'صحت کا ریکارڈ', recentActivity: 'حالیہ صحت کی سرگرمی', refresh: 'تازہ کریں', loadingActivity: 'صحت کا ریکارڈ دیکھا جا رہا ہے…',
      noAssessments: 'ابھی تک صحت کا کوئی معائنہ موجود نہیں ہے۔', startFirstAssessment: 'پہلا معائنہ شروع کریں', viewResult: 'نتیجہ دیکھیں',
      activityUnavailable: 'صحت کا ریکارڈ ابھی نہیں دکھایا جا سکتا۔', animalHealth: 'جانور کی صحت', quickActions: 'فوری کام',
      startAssessment: 'صحت کا معائنہ شروع کریں', assessmentHelp: 'تصویر اور علامات کے ساتھ', healthHistory: 'صحت کی پچھلی تفصیل',
      preventiveCare: 'بیماری سے بچاؤ', followUp: 'دوبارہ جانچ', healthPassport: 'صحت پاسپورٹ', comingSoon: 'جلد آرہا ہے',
      upcomingCare: 'قریب کی دیکھ بھال', upcomingCareHelp: 'گزری ہوئی، آج کی اور اگلے 10 دن کی یاد دہانیاں', viewAllReminders: 'تمام یاد دہانیاں دیکھیں', reminderOverdue: 'تاریخ گزر چکی ہے', reminderDueToday: 'آج کی تاریخ', reminderDueTomorrow: 'کل کی تاریخ', reminderDueInDays: '{count} دن بعد',
      recordSettings: 'ریکارڈ کی ترتیب', deleteHelp: 'اگر یہ ریکارڈ مزید نہیں چاہیے تو اسے حذف کر سکتے ہیں۔', deleteAnimal: 'جانور کا ریکارڈ حذف کریں',
      footerCare: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔', footerDisclaimer: 'AI کی رائے ابتدائی رہنمائی ہے، ڈاکٹر کا متبادل نہیں۔',
      editRecord: 'ریکارڈ میں تبدیلی', closeFormLabel: 'فارم بند کریں', name: 'نام', notRecorded: 'درج نہیں', female: 'مادہ', male: 'نر',
      ageYears: 'عمر (سال)', weightKg: 'وزن (کلو)', healthy: 'صحت مند', needsAttention: 'توجہ درکار', underTreatment: 'علاج جاری ہے',
      cancel: 'منسوخ کریں', saveChanges: 'تبدیلی محفوظ کریں', saving: 'محفوظ ہو رہا ہے…', assessmentInstructions: 'جانور کی صاف تصویر دیں، پھر علامات لکھیں یا اردو میں بولیں۔',
      animalPhoto: 'جانور کی تصویر', uploadImage: 'تصویر اپ لوڈ کریں', takePhoto: 'تصویر لیں', noImageSelected: 'ابھی کوئی تصویر منتخب نہیں ہوئی۔', selectedImage: 'منتخب تصویر: {name}', imageRequired: 'براہِ کرم تصویر اپ لوڈ کریں یا نئی تصویر لیں۔', imageHelp: 'JPG، PNG یا WebP — زیادہ سے زیادہ 5 MB', symptoms: 'علامات',
      symptomsPlaceholder: 'مثلاً جانور کھانا نہیں کھا رہا اور سست ہے', assessmentSafety: 'یہ ابتدائی AI رہنمائی ہے۔ ہنگامی حالت میں فوراً جانوروں کے ڈاکٹر سے رابطہ کریں۔',
      beginAssessment: 'معائنہ کریں', assessing: 'معائنہ ہو رہا ہے…', assessmentProcessingTitle: 'تصویر اور علامات دیکھی جا رہی ہیں…', assessmentProcessingHelp: 'معائنہ تیار ہو رہا ہے، براہِ کرم تھوڑا انتظار کریں۔', deleteQuestion: 'کیا یہ جانور حذف کرنا ہے؟',
      deleteWarning: 'اس جانور کا ریکارڈ ختم ہو جائے گا۔ یہ عمل واپس نہیں ہو سکتا۔', keepAnimal: 'ریکارڈ رہنے دیں', confirmDelete: 'ہاں، حذف کریں', deleting: 'حذف ہو رہا ہے…',
      pageNotFound: 'جانور کا ریکارڈ نہیں ملا', notFoundMessage: 'یہ ریکارڈ موجود نہیں یا حذف ہو چکا ہے۔', forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ ریکارڈ دیکھنے کی اجازت نہیں ہے۔', connectionTitle: 'ریکارڈ ابھی دستیاب نہیں',
      connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔', recordNumber: 'ریکارڈ', updatedOn: 'آخری تبدیلی',
      noNotes: 'کوئی نوٹ درج نہیں کیا گیا۔', year: 'سال', kg: 'کلو', recordUpdated: 'جانور کی معلومات محفوظ ہو گئیں۔',
      assessmentSaved: 'صحت کا معائنہ ریکارڈ ہو گیا۔', couldNotSave: 'معلومات محفوظ نہیں ہو سکیں۔ دوبارہ کوشش کریں۔',
      couldNotAssess: 'معائنہ مکمل نہیں ہو سکا۔ دوبارہ کوشش کریں۔', couldNotDelete: 'ریکارڈ حذف نہیں ہو سکا۔ دوبارہ کوشش کریں۔',
      imageTooLarge: 'تصویر 5 MB سے کم ہونی چاہیے۔', imageBlurry: 'تصویر دھندلی ہے۔ براہِ کرم صاف تصویر منتخب کر کے دوبارہ کوشش کریں۔', imageDark: 'تصویر بہت تاریک ہے۔ براہِ کرم بہتر روشنی میں تصویر لے کر دوبارہ کوشش کریں۔', imageLowResolution: 'تصویر کی کوالٹی بہت کم ہے۔ براہِ کرم زیادہ واضح تصویر منتخب کر کے دوبارہ کوشش کریں۔', imageUnreadable: 'تصویر پڑھی نہیں جا سکی۔ براہِ کرم دوسری JPG، PNG یا WebP تصویر منتخب کریں۔', imageInvalidType: 'تصویر کا فارمیٹ درست نہیں۔ براہِ کرم JPG، PNG یا WebP تصویر منتخب کریں۔',
      statusPending: 'جاری ہے', statusCompleted: 'مکمل', statusFailed: 'مکمل نہیں ہوا',
      urgencyLow: 'معمولی توجہ', urgencyMedium: 'توجہ درکار', urgencyHigh: 'فوری توجہ', noConditionSummary: 'کوئی بیماری درج نہیں',
      preliminaryResult: 'ابتدائی نتیجہ', assessmentDate: 'معائنے کی تاریخ', symptomMethod: 'علامات بتانے کا طریقہ', typeSymptoms: 'علامات لکھیں', speakUrdu: 'اردو میں بولیں', recordingPreviewLabel: 'ریکارڈ کی گئی آواز سنیں',
      voiceReady: 'ریکارڈ کرنے کے لیے تیار', voiceReadyHelp: 'مائیک دبائیں اور جانور کی علامات صاف آواز میں اردو میں بتائیں۔', accessingMicrophone: 'مائیک کھولا جا رہا ہے…', accessingMicrophoneHelp: 'اجازت مانگے جانے پر مائیک استعمال کرنے کی اجازت دیں۔',
      voiceRecording: 'آواز ریکارڈ ہو رہی ہے…', voiceRecordingHelp: 'علامات بتا کر ریکارڈنگ روکیں۔', voiceComplete: 'آواز ریکارڈ ہو گئی', voiceCompleteHelp: 'آپ آواز سن سکتے ہیں یا دوبارہ ریکارڈ کر سکتے ہیں۔',
      startRecording: 'ریکارڈنگ شروع کریں', stopRecording: 'ریکارڈنگ روکیں', recordAgain: 'دوبارہ ریکارڈ کریں', microphoneDenied: 'مائیک کی اجازت نہیں ملی', microphoneDeniedHelp: 'براؤزر میں مائیک کی اجازت دیں، پھر دوبارہ کوشش کریں۔', microphoneUnavailable: 'مائیک استعمال نہیں ہو سکا', microphoneUnavailableHelp: 'اس ڈیوائس یا براؤزر میں مائیک دستیاب نہیں ہے۔', recordingUnsupported: 'اس براؤزر میں آواز ریکارڈ نہیں ہو سکتی', recordingUnsupportedHelp: 'نیا Chrome، Edge، Firefox یا Safari براؤزر استعمال کریں۔', recordingFailed: 'آواز ریکارڈ نہیں ہو سکی', recordingFailedHelp: 'دوبارہ کوشش کریں یا علامات لکھ دیں۔',
      submitVoiceAssessment: 'آواز کے ساتھ معائنہ کریں', processingVoice: 'آواز سمجھی جا رہی ہے…', audioRequired: 'پہلے اپنی آواز ریکارڈ کریں۔', voiceNoSpeech: 'آواز میں بات صاف سمجھ نہیں آئی۔ دوبارہ صاف آواز میں علامات بتائیں۔', voiceInvalidAudio: 'ریکارڈ کی گئی آواز درست نہیں۔ براہِ کرم دوبارہ ریکارڈ کریں۔', voiceRecognitionUnavailable: 'آواز ابھی سمجھی نہیں جا سکی۔ کچھ دیر بعد دوبارہ کوشش کریں۔', voiceConnectionUnavailable: 'رابطہ نہیں ہو سکا۔ اپنی آواز محفوظ رکھیں اور دوبارہ کوشش کریں۔'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language',
      backToAnimals: 'Back to animals', backToAnimalsShort: 'Animal dashboard', loadingLabel: 'Loading animal record', tryAgain: 'Try again', logout: 'Logout',
      editAnimal: 'Edit animal', profileDetails: 'Animal details', basicInformation: 'Basic information', animalType: 'Animal type', breed: 'Breed',
      gender: 'Gender', age: 'Age', weight: 'Weight', color: 'Color', region: 'Region', healthStatus: 'Current health status', recordCreated: 'Record created',
      careNotes: 'Care notes', notes: 'Notes', healthRecord: 'Health record', recentActivity: 'Recent health activity', refresh: 'Refresh',
      loadingActivity: 'Loading health activity…', noAssessments: 'No health assessments yet.', startFirstAssessment: 'Start the first assessment', viewResult: 'View Result',
      activityUnavailable: 'Health activity cannot be shown right now.', animalHealth: 'Animal health', quickActions: 'Quick actions',
      startAssessment: 'Start Health Assessment', assessmentHelp: 'With a photo and symptoms', healthHistory: 'Health History', preventiveCare: 'Preventive Care',
      followUp: 'Follow-Up', healthPassport: 'Health Passport', comingSoon: 'Coming soon', recordSettings: 'Record settings',
      upcomingCare: 'Upcoming care', upcomingCareHelp: 'Overdue, due today and reminders within the next 10 days', viewAllReminders: 'View all reminders', reminderOverdue: 'Overdue', reminderDueToday: 'Due today', reminderDueTomorrow: 'Due tomorrow', reminderDueInDays: 'Due in {count} days',
      deleteHelp: 'If this record is no longer needed, you can remove it.', deleteAnimal: 'Delete animal record',
      footerCare: 'Built to support better livestock care.', footerDisclaimer: 'AI guidance is preliminary and does not replace a veterinarian.',
      editRecord: 'Edit record', closeFormLabel: 'Close form', name: 'Name', notRecorded: 'Not recorded', female: 'Female', male: 'Male',
      ageYears: 'Age in years', weightKg: 'Weight in kg', healthy: 'Healthy', needsAttention: 'Needs attention', underTreatment: 'Under treatment',
      cancel: 'Cancel', saveChanges: 'Save changes', saving: 'Saving…', assessmentInstructions: 'Add a clear animal photo, then type the symptoms or speak in Urdu.',
      animalPhoto: 'Animal photo', uploadImage: 'Upload image', takePhoto: 'Take photo', noImageSelected: 'No image selected yet.', selectedImage: 'Selected image: {name}', imageRequired: 'Please upload an image or take a new photo.', imageHelp: 'JPG, PNG or WebP — maximum 5 MB', symptoms: 'Symptoms',
      symptomsPlaceholder: 'e.g. The animal is not eating and seems tired', assessmentSafety: 'This is preliminary AI guidance. Contact a veterinarian immediately in an emergency.',
      beginAssessment: 'Begin assessment', assessing: 'Assessing…', assessmentProcessingTitle: 'Reviewing the photo and symptoms…', assessmentProcessingHelp: 'Your assessment is being prepared. Please wait a moment.', deleteQuestion: 'Delete this animal?',
      deleteWarning: 'This will remove this animal record. This action cannot be undone.', keepAnimal: 'Keep animal', confirmDelete: 'Yes, delete', deleting: 'Deleting…',
      pageNotFound: 'Animal record not found', notFoundMessage: 'This record does not exist or may have been removed.', forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to access this record.', connectionTitle: 'Record unavailable right now',
      connectionMessage: 'We could not connect. Please try again in a little while.', recordNumber: 'Record', updatedOn: 'Last updated',
      noNotes: 'No notes recorded.', year: 'yr', kg: 'kg', recordUpdated: 'Animal information was saved.',
      assessmentSaved: 'The health assessment was recorded.', couldNotSave: 'The information could not be saved. Please try again.',
      couldNotAssess: 'The assessment could not be completed. Please try again.', couldNotDelete: 'The record could not be deleted. Please try again.',
      imageTooLarge: 'The image must be smaller than 5 MB. Please choose another image and try again.', imageBlurry: 'Image is too blurry to analyze. Please upload a clearer photo.', imageDark: 'Image is too dark. Please choose a brighter photo and try again.', imageLowResolution: 'Image resolution is too low. Please choose a clearer, higher-resolution photo and try again.', imageUnreadable: 'Image could not be processed. Please choose another JPG, PNG or WebP image.', imageInvalidType: 'This image format is not accepted. Please choose a JPG, PNG or WebP image.',
      statusPending: 'Pending', statusCompleted: 'Completed', statusFailed: 'Not completed',
      urgencyLow: 'Low urgency', urgencyMedium: 'Needs attention', urgencyHigh: 'Urgent attention', noConditionSummary: 'No condition recorded',
      preliminaryResult: 'Preliminary result', assessmentDate: 'Assessment date', symptomMethod: 'How would you describe the symptoms?', typeSymptoms: 'Type Symptoms', speakUrdu: 'Speak in Urdu', recordingPreviewLabel: 'Listen to the recorded symptoms',
      voiceReady: 'Ready to record', voiceReadyHelp: 'Press the microphone and describe the animal’s symptoms clearly in Urdu.', accessingMicrophone: 'Opening microphone…', accessingMicrophoneHelp: 'Allow microphone access when your browser asks.',
      voiceRecording: 'Recording…', voiceRecordingHelp: 'Describe the symptoms, then stop the recording.', voiceComplete: 'Recording complete', voiceCompleteHelp: 'You can listen to the recording or record it again.',
      startRecording: 'Start recording', stopRecording: 'Stop recording', recordAgain: 'Re-record', microphoneDenied: 'Microphone permission was not allowed', microphoneDeniedHelp: 'Allow microphone access in your browser, then try again.', microphoneUnavailable: 'Microphone unavailable', microphoneUnavailableHelp: 'A microphone is not available on this device or browser.', recordingUnsupported: 'Voice recording is not supported in this browser', recordingUnsupportedHelp: 'Please use a recent version of Chrome, Edge, Firefox or Safari.', recordingFailed: 'The recording could not be completed', recordingFailedHelp: 'Please try again or type the symptoms instead.',
      submitVoiceAssessment: 'Assess with Voice', processingVoice: 'Understanding your recording…', audioRequired: 'Please record your symptoms first.', voiceNoSpeech: 'We could not understand clear speech in the recording. Please record the symptoms again.', voiceInvalidAudio: 'The recorded audio could not be used. Please record it again.', voiceRecognitionUnavailable: 'We could not understand the recording right now. Please try again shortly.', voiceConnectionUnavailable: 'We could not connect. Your recording is still ready, so please try again.'
    }
  };

  const el = {
    loading: document.querySelector('#profile-loading'), error: document.querySelector('#profile-error'), content: document.querySelector('#profile-content'),
    errorTitle: document.querySelector('#profile-error-title'), errorMessage: document.querySelector('#profile-error-message'), feedback: document.querySelector('#page-feedback'),
    name: document.querySelector('#animal-name'), kind: document.querySelector('#animal-kind'), typeIcon: document.querySelector('#animal-type-icon'),
    healthBadge: document.querySelector('#animal-health-badge'), idLabel: document.querySelector('#animal-id-label'), updated: document.querySelector('#updated-date'),
    infoType: document.querySelector('#info-type'), infoBreed: document.querySelector('#info-breed'), infoGender: document.querySelector('#info-gender'),
    infoAge: document.querySelector('#info-age'), infoWeight: document.querySelector('#info-weight'), infoColor: document.querySelector('#info-color'), infoRegion: document.querySelector('#info-region'),
    infoHealth: document.querySelector('#info-health'), created: document.querySelector('#created-date'), notes: document.querySelector('#animal-notes'),
    activityLoading: document.querySelector('#activity-loading'), activityList: document.querySelector('#activity-list'), activityEmpty: document.querySelector('#activity-empty'),
    activityError: document.querySelector('#activity-error'), editDialog: document.querySelector('#edit-dialog'), editForm: document.querySelector('#edit-form'),
    editAlert: document.querySelector('#edit-alert'), saveEdit: document.querySelector('#save-edit'), assessmentDialog: document.querySelector('#assessment-dialog'),
    assessmentForm: document.querySelector('#assessment-form'), assessmentAlert: document.querySelector('#assessment-alert'), assessmentProcessing: document.querySelector('#assessment-processing'), submitAssessment: document.querySelector('#submit-assessment'),
    uploadInput: document.querySelector('#assessment-upload-input'), cameraInput: document.querySelector('#assessment-camera-input'), imageSelection: document.querySelector('#assessment-image-selection'),
    typedPanel: document.querySelector('#typed-symptoms-panel'), voicePanel: document.querySelector('#voice-symptoms-panel'), symptomsInput: document.querySelector('[name="symptoms"]'),
    voiceTitle: document.querySelector('#voice-state-title'), voiceHelp: document.querySelector('#voice-state-help'), voiceTimer: document.querySelector('#voice-timer'), voicePreview: document.querySelector('#voice-preview'),
    startRecording: document.querySelector('#start-voice-recording'), stopRecording: document.querySelector('#stop-voice-recording'), rerecord: document.querySelector('#rerecord-voice'),
    deleteDialog: document.querySelector('#delete-dialog'), deleteAlert: document.querySelector('#delete-alert'), confirmDelete: document.querySelector('#confirm-delete'),
    historyLink: document.querySelector('#health-history-link'), preventiveLink: document.querySelector('#preventive-care-link'), passportLink: document.querySelector('#health-passport-link'),
    reminderStrip: document.querySelector('#profile-reminders'), reminderList: document.querySelector('#profile-reminder-list'), reminderListLink: document.querySelector('#profile-reminders-link')
  };

  let language = window.MaweshiI18n.getLanguage();
  let animal = null;
  let assessments = [];
  let reminders = [];
  let pageErrorKind = null;
  let assessmentMode = 'typed';
  let voiceState = 'idle';
  let audioBlob = null;
  let audioObjectUrl = '';
  let mediaRecorder = null;
  let microphoneStream = null;
  let recordingChunks = [];
  let recordingStartedAt = 0;
  let recordingTimer = null;
  let recordingRequestId = 0;
  let assessmentSubmitting = false;

  class RequestError extends Error {
    constructor(message, status, details) { super(message); this.status = status; this.details = details; }
  }

  function t(key) { return copy[language][key] || key; }

  const api = {
    getAnimal: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, { headers: { Accept: 'application/json' } }),
    getAssessments: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/assessments`, { headers: { Accept: 'application/json' } }),
    getReminders: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/reminders`, { headers: { Accept: 'application/json' } }),
    updateAnimal: (id, payload) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload)
    }),
    deleteAnimal: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, { method: 'DELETE', headers: { Accept: 'application/json' } }),
    createAssessment: (id, formData) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/assessments`, { method: 'POST', body: formData }),
    createVoiceAssessment: (id, formData) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/symptoms/voice`, { method: 'POST', body: formData })
  };

  function translatePage() {
    language = window.MaweshiI18n.applyPage(language, copy).language;
    if (animal) renderAnimal();
    if (assessments.length) renderAssessments();
    renderProfileReminders();
    if (pageErrorKind !== null) showPageError(pageErrorKind);
    updateImageSelection();
    renderVoiceState();
    updateAssessmentSubmitButton();
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

  function parseReminderDate(raw) {
    if (typeof raw !== 'string' || !raw.trim()) return null;
    const value = raw.trim();
    const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
    const date = dateOnly
      ? new Date(Number(dateOnly[1]), Number(dateOnly[2]) - 1, Number(dateOnly[3]))
      : new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function calendarDayNumber(date) { return Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) / 86400000; }
  function daysUntilReminder(date) { return calendarDayNumber(date) - calendarDayNumber(new Date()); }

  function reminderTimingLabel(days) {
    if (days < 0) return t('reminderOverdue');
    if (days === 0) return t('reminderDueToday');
    if (days === 1) return t('reminderDueTomorrow');
    return t('reminderDueInDays').replace('{count}', new Intl.NumberFormat(language === 'ur' ? 'ur-PK' : 'en-PK').format(days));
  }

  function formatReminderDate(date) {
    return new Intl.DateTimeFormat(language === 'ur' ? 'ur-PK' : 'en-PK', { day: 'numeric', month: 'short', year: 'numeric' }).format(date);
  }

  function renderProfileReminders() {
    el.reminderStrip.classList.add('hidden');
    el.reminderStrip.classList.remove('has-overdue');
    el.reminderList.replaceChildren();
    const relevant = reminders
      .map((record) => ({ record, date: parseReminderDate(record?.due_date) }))
      .filter(({ record, date }) => record && date && String(record.reminder_type || '').trim())
      .map((item) => ({ ...item, days: daysUntilReminder(item.date) }))
      .filter(({ days }) => days <= 10)
      .sort((a, b) => {
        const aGroup = a.days < 0 ? 0 : a.days === 0 ? 1 : 2;
        const bGroup = b.days < 0 ? 0 : b.days === 0 ? 1 : 2;
        if (aGroup !== bGroup) return aGroup - bGroup;
        return aGroup === 0 ? b.days - a.days : a.days - b.days;
      })
      .slice(0, 3);
    if (!relevant.length) return;
    const fragment = document.createDocumentFragment();
    relevant.forEach(({ record, date, days }) => {
      const item = document.createElement('li');
      item.className = `profile-reminder-item profile-reminder-item--${days < 0 ? 'overdue' : days === 0 ? 'today' : 'upcoming'}`;
      const status = document.createElement('span');
      status.className = 'profile-reminder-status';
      status.textContent = reminderTimingLabel(days);
      const type = document.createElement('strong');
      type.textContent = String(record.reminder_type).trim();
      const due = document.createElement('time');
      due.dateTime = String(record.due_date || '');
      due.textContent = formatReminderDate(date);
      item.append(status, type, due);
      if (record.notes && String(record.notes).trim()) {
        const notes = document.createElement('p');
        notes.textContent = String(record.notes).trim();
        item.appendChild(notes);
      }
      fragment.appendChild(item);
    });
    el.reminderList.appendChild(fragment);
    el.reminderStrip.classList.toggle('has-overdue', relevant.some(({ days }) => days < 0));
    el.reminderStrip.classList.remove('hidden');
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
    el.infoRegion.textContent = value(animal.region);
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
      loadReminders();
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
    ['name', 'animal_type', 'breed', 'gender', 'age', 'weight', 'color', 'region', 'health_status', 'notes'].forEach((field) => setFormValue(el.editForm, field, animal[field]));
    el.editAlert.classList.add('hidden'); el.editDialog.showModal();
  }
  function optional(formData, key) { const raw = String(formData.get(key) || '').trim(); return raw || null; }
  function editPayload() {
    const data = new FormData(el.editForm);
    const payload = { name: String(data.get('name') || '').trim(), animal_type: String(data.get('animal_type') || '').trim() };
    ['breed', 'gender', 'color', 'region', 'health_status', 'notes'].forEach((key) => { payload[key] = optional(data, key); });
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

  function supportedRecordingType() {
    if (!window.MediaRecorder || typeof window.MediaRecorder.isTypeSupported !== 'function') return null;
    const candidates = [
      { mimeType: 'audio/webm;codecs=opus', extension: 'webm' },
      { mimeType: 'audio/webm', extension: 'webm' },
      { mimeType: 'audio/ogg;codecs=opus', extension: 'ogg' },
      { mimeType: 'audio/ogg', extension: 'ogg' },
      { mimeType: 'audio/mp4', extension: 'm4a' }
    ];
    return candidates.find((candidate) => window.MediaRecorder.isTypeSupported(candidate.mimeType)) || null;
  }

  function releaseMicrophone() {
    if (microphoneStream) microphoneStream.getTracks().forEach((track) => track.stop());
    microphoneStream = null;
    window.clearInterval(recordingTimer);
    recordingTimer = null;
  }

  function clearRecordedAudio() {
    audioBlob = null;
    recordingChunks = [];
    if (audioObjectUrl) URL.revokeObjectURL(audioObjectUrl);
    audioObjectUrl = '';
    el.voicePreview.removeAttribute('src');
    el.voicePreview.load();
  }

  function resetVoiceRecording() {
    recordingRequestId += 1;
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.ondataavailable = null;
      mediaRecorder.onstop = null;
      mediaRecorder.onerror = null;
      mediaRecorder.stop();
    }
    mediaRecorder = null;
    releaseMicrophone();
    clearRecordedAudio();
    voiceState = 'idle';
    renderVoiceState();
  }

  function voiceStateCopy() {
    if (voiceState === 'requesting') return ['accessingMicrophone', 'accessingMicrophoneHelp'];
    if (voiceState === 'recording') return ['voiceRecording', 'voiceRecordingHelp'];
    if (voiceState === 'ready') return ['voiceComplete', 'voiceCompleteHelp'];
    if (voiceState === 'denied') return ['microphoneDenied', 'microphoneDeniedHelp'];
    if (voiceState === 'unavailable') return ['microphoneUnavailable', 'microphoneUnavailableHelp'];
    if (voiceState === 'unsupported') return ['recordingUnsupported', 'recordingUnsupportedHelp'];
    if (voiceState === 'error') return ['recordingFailed', 'recordingFailedHelp'];
    return ['voiceReady', 'voiceReadyHelp'];
  }

  function formatRecordingTime(milliseconds) {
    const totalSeconds = Math.max(0, Math.floor(milliseconds / 1000));
    return `${String(Math.floor(totalSeconds / 60)).padStart(2, '0')}:${String(totalSeconds % 60).padStart(2, '0')}`;
  }

  function renderVoiceState() {
    if (!el.voicePanel) return;
    const [titleKey, helpKey] = voiceStateCopy();
    el.voiceTitle.textContent = t(titleKey);
    el.voiceHelp.textContent = t(helpKey);
    el.voicePanel.classList.toggle('is-recording', voiceState === 'recording');
    el.voicePanel.classList.toggle('is-ready', voiceState === 'ready');
    el.voiceTimer.classList.toggle('hidden', voiceState !== 'recording');
    el.startRecording.classList.toggle('hidden', voiceState === 'recording' || voiceState === 'ready' || voiceState === 'requesting');
    el.stopRecording.classList.toggle('hidden', voiceState !== 'recording');
    el.rerecord.classList.toggle('hidden', voiceState !== 'ready');
    el.voicePreview.classList.toggle('hidden', voiceState !== 'ready' || !audioObjectUrl);
    el.startRecording.disabled = voiceState === 'requesting' || assessmentSubmitting;
    el.stopRecording.disabled = assessmentSubmitting;
    el.rerecord.disabled = assessmentSubmitting;
  }

  function updateAssessmentSubmitButton() {
    el.submitAssessment.disabled = assessmentSubmitting || voiceState === 'recording' || voiceState === 'requesting';
    document.querySelectorAll('[data-assessment-mode]').forEach((button) => { button.disabled = assessmentSubmitting; });
    el.assessmentProcessing.classList.toggle('hidden', !assessmentSubmitting);
    if (assessmentSubmitting) el.assessmentForm.setAttribute('aria-busy', 'true');
    else el.assessmentForm.removeAttribute('aria-busy');
    el.submitAssessment.textContent = t(assessmentSubmitting
      ? assessmentMode === 'voice' ? 'processingVoice' : 'assessing'
      : assessmentMode === 'voice' ? 'submitVoiceAssessment' : 'beginAssessment');
  }

  function setAssessmentMode(mode) {
    if (assessmentSubmitting || !['typed', 'voice'].includes(mode) || assessmentMode === mode) return;
    if (assessmentMode === 'voice') resetVoiceRecording();
    assessmentMode = mode;
    const isVoice = mode === 'voice';
    el.typedPanel.classList.toggle('hidden', isVoice);
    el.voicePanel.classList.toggle('hidden', !isVoice);
    el.symptomsInput.disabled = isVoice;
    el.symptomsInput.required = !isVoice;
    document.querySelectorAll('[data-assessment-mode]').forEach((button) => {
      const selected = button.dataset.assessmentMode === mode;
      button.classList.toggle('is-active', selected);
      button.setAttribute('aria-selected', String(selected));
      button.tabIndex = selected ? 0 : -1;
    });
    el.assessmentAlert.classList.add('hidden');
    renderVoiceState();
    updateAssessmentSubmitButton();
  }

  async function startVoiceRecording() {
    el.assessmentAlert.classList.add('hidden');
    const recordingType = supportedRecordingType();
    if (!recordingType || !navigator.mediaDevices?.getUserMedia) {
      voiceState = 'unsupported'; renderVoiceState(); return;
    }
    clearRecordedAudio();
    voiceState = 'requesting'; renderVoiceState(); updateAssessmentSubmitButton();
    const requestId = ++recordingRequestId;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true }, video: false });
      if (requestId !== recordingRequestId || assessmentMode !== 'voice') { stream.getTracks().forEach((track) => track.stop()); return; }
      microphoneStream = stream;
      recordingChunks = [];
      mediaRecorder = new MediaRecorder(stream, { mimeType: recordingType.mimeType });
      mediaRecorder.ondataavailable = (event) => { if (event.data?.size) recordingChunks.push(event.data); };
      mediaRecorder.onerror = () => {
        if (mediaRecorder) mediaRecorder.onstop = null;
        releaseMicrophone(); mediaRecorder = null; voiceState = 'error'; renderVoiceState(); updateAssessmentSubmitButton();
      };
      mediaRecorder.onstop = () => {
        const mimeType = mediaRecorder?.mimeType || recordingType.mimeType;
        releaseMicrophone(); mediaRecorder = null;
        audioBlob = new Blob(recordingChunks, { type: mimeType });
        recordingChunks = [];
        if (!audioBlob.size) { audioBlob = null; voiceState = 'error'; }
        else {
          audioObjectUrl = URL.createObjectURL(audioBlob);
          el.voicePreview.src = audioObjectUrl;
          voiceState = 'ready';
        }
        renderVoiceState(); updateAssessmentSubmitButton();
      };
      mediaRecorder.start(250);
      recordingStartedAt = Date.now();
      el.voiceTimer.textContent = '00:00';
      recordingTimer = window.setInterval(() => { el.voiceTimer.textContent = formatRecordingTime(Date.now() - recordingStartedAt); }, 500);
      voiceState = 'recording'; renderVoiceState(); updateAssessmentSubmitButton();
    } catch (error) {
      console.error('Microphone recording could not start.', error);
      releaseMicrophone(); mediaRecorder = null;
      voiceState = error?.name === 'NotAllowedError' || error?.name === 'SecurityError' ? 'denied' : error?.name === 'NotFoundError' ? 'unavailable' : 'error';
      renderVoiceState(); updateAssessmentSubmitButton();
    }
  }

  async function loadReminders() {
    try {
      const data = await api.getReminders(animalId);
      reminders = Array.isArray(data) ? data : [];
      renderProfileReminders();
    } catch (error) {
      console.error('Animal reminders could not be loaded.', error);
      reminders = [];
      renderProfileReminders();
    }
  }

  function stopVoiceRecording() {
    if (mediaRecorder?.state === 'recording') mediaRecorder.stop();
  }

  function openAssessment() {
    el.assessmentAlert.classList.add('hidden');
    updateImageSelection();
    renderVoiceState();
    updateAssessmentSubmitButton();
    el.assessmentDialog.showModal();
  }

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

  function voiceAssessmentErrorMessage(error) {
    const candidates = [error?.payload?.message, error?.payload?.error, error?.message, error?.details]
      .flat().filter((item) => typeof item === 'string').join(' ');
    if (candidates.includes('No understandable speech was detected')) return t('voiceNoSpeech');
    if (candidates.includes('Unsupported audio format') || candidates.includes('Unrecognised audio format') || candidates.includes('audio file is empty')) return t('voiceInvalidAudio');
    if (candidates.includes("'audio' file field is required")) return t('audioRequired');
    if (candidates.includes("'image' file field is required")) return t('imageRequired');
    if (error?.status === 502 || candidates.includes('Speech transcription is currently unavailable')) return t('voiceRecognitionUnavailable');
    if (error?.status === 0) return t('voiceConnectionUnavailable');
    return '';
  }

  function audioFilename(blob) {
    const mimeType = String(blob?.type || '').toLowerCase();
    if (mimeType.includes('ogg')) return 'urdu-symptoms.ogg';
    if (mimeType.includes('mp4')) return 'urdu-symptoms.m4a';
    if (mimeType.includes('mpeg')) return 'urdu-symptoms.mp3';
    if (mimeType.includes('wav')) return 'urdu-symptoms.wav';
    return 'urdu-symptoms.webm';
  }

  async function submitAssessment(event) {
    event.preventDefault(); el.assessmentAlert.classList.add('hidden');
    if (assessmentMode === 'typed' && !el.assessmentForm.reportValidity()) return;
    const image = selectedAssessmentImage();
    if (!image) { el.assessmentAlert.textContent = t('imageRequired'); el.assessmentAlert.classList.remove('hidden'); return; }
    if (image.size > MAX_IMAGE_BYTES) { el.assessmentAlert.textContent = t('imageTooLarge'); el.assessmentAlert.classList.remove('hidden'); return; }
    if (assessmentMode === 'voice' && (!audioBlob || !audioBlob.size)) { el.assessmentAlert.textContent = t('audioRequired'); el.assessmentAlert.classList.remove('hidden'); return; }
    const data = new FormData();
    data.set('image', image, image.name || 'animal-photo.jpg');
    if (assessmentMode === 'voice') data.set('audio', audioBlob, audioFilename(audioBlob));
    else data.set('symptoms', el.symptomsInput.value.trim());
    const submittedMode = assessmentMode;
    assessmentSubmitting = true; renderVoiceState(); updateAssessmentSubmitButton();
    try {
      const response = submittedMode === 'voice'
        ? await api.createVoiceAssessment(animalId, data)
        : await api.createAssessment(animalId, data);
      const assessment = submittedMode === 'voice' ? response?.assessment : response;
      if (!assessment || assessment.id === null || assessment.id === undefined || String(assessment.id).trim() === '') {
        throw new RequestError('Assessment id missing', 200);
      }
      if (submittedMode === 'voice' && typeof response.transcribed_symptoms !== 'string') {
        throw new RequestError('Transcription missing', 200);
      }
      el.assessmentForm.reset();
      el.uploadInput.value = '';
      el.cameraInput.value = '';
      updateImageSelection();
      window.location.assign(`assessment-result.html?id=${encodeURIComponent(assessment.id)}`);
    } catch (error) {
      console.error(error);
      el.assessmentAlert.textContent = assessmentImageErrorMessage(error) || (submittedMode === 'voice' ? voiceAssessmentErrorMessage(error) : '') || t('couldNotAssess');
      el.assessmentAlert.classList.remove('hidden');
    } finally { assessmentSubmitting = false; renderVoiceState(); updateAssessmentSubmitButton(); }
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
    const assessmentModeButton = event.target.closest('[data-assessment-mode]');
    if (assessmentModeButton) setAssessmentMode(assessmentModeButton.dataset.assessmentMode);
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
  el.startRecording.addEventListener('click', startVoiceRecording);
  el.stopRecording.addEventListener('click', stopVoiceRecording);
  el.rerecord.addEventListener('click', startVoiceRecording);
  el.assessmentDialog.addEventListener('close', () => {
    setAssessmentMode('typed');
  });
  el.confirmDelete.addEventListener('click', deleteAnimal);

  el.historyLink.href = animalId ? `health-history.html?id=${encodeURIComponent(animalId)}` : 'index.html';
  el.preventiveLink.href = animalId ? `preventive-care.html?id=${encodeURIComponent(animalId)}` : 'index.html';
  el.reminderListLink.href = animalId ? `preventive-care.html?id=${encodeURIComponent(animalId)}` : 'index.html';
  el.passportLink.href = animalId ? `health-passport.html?id=${encodeURIComponent(animalId)}` : 'index.html';
  setAssessmentMode('typed');
  translatePage();
  loadProfile();
})();
