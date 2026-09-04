(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const animalId = new URLSearchParams(window.location.search).get('id');

  const copy = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں', logout: 'لاگ آؤٹ', backToProfile: 'جانور کے پروفائل پر واپس جائیں',
      loadingLabel: 'یاد دہانیاں دیکھی جا رہی ہیں', tryAgain: 'دوبارہ کوشش کریں', pageTitle: 'بیماری سے بچاؤ اور یاد دہانیاں', pageSubtitle: 'ویکسین، پیٹ کے کیڑوں کی دوا اور معمول کے معائنے کی تاریخیں یاد رکھیں۔',
      addReminder: 'یاد دہانی شامل کریں', careSchedule: 'دیکھ بھال کی تاریخیں', allReminders: 'تمام یاد دہانیاں', reminderCount: '{count} یاد دہانیاں', oneReminder: '1 یاد دہانی',
      emptyTitle: 'ابھی بیماری سے بچاؤ کی کوئی یاد دہانی نہیں ہے۔', emptyHelp: 'اگلی ویکسین، پیٹ کے کیڑوں کی دوا یا معمول کے معائنے کی تاریخ شامل کریں۔',
      reminderDistinction: 'یہ صرف یاد دہانیاں ہیں۔ یہ کسی ویکسین یا علاج کے مکمل ہونے کا طبی ریکارڈ نہیں ہیں۔', preventiveCare: 'بیماری سے بچاؤ', formHelp: 'جانور کی اگلی ضروری دیکھ بھال کی تاریخ لکھیں۔',
      reminderType: 'یاد دہانی کی قسم', typePlaceholder: 'مثلاً ویکسین', typeHelp: 'اپنی ضرورت کے مطابق کوئی بھی مختصر نام لکھ سکتے ہیں۔', dueDate: 'یاد دہانی کی تاریخ', notes: 'نوٹس (اختیاری)', notesPlaceholder: 'مثلاً پچھلی خوراک یا ڈاکٹر کی ہدایت', notesHelp: 'یہ نوٹ جیسے لکھیں گے ویسے ہی محفوظ ہوگا۔',
      cancel: 'منسوخ کریں', saveReminder: 'یاد دہانی محفوظ کریں', saving: 'محفوظ ہو رہی ہے…', closeFormLabel: 'فارم بند کریں', typeRequired: 'یاد دہانی کی قسم لکھیں۔', dateRequired: 'یاد دہانی کی تاریخ منتخب کریں۔',
      reminderSaved: 'یاد دہانی محفوظ ہو گئی۔', createFailed: 'یاد دہانی محفوظ نہیں ہو سکی۔ معلومات دیکھ کر دوبارہ کوشش کریں۔',
      upcoming: 'آنے والی', dueToday: 'آج کی تاریخ', overdue: 'تاریخ گزر چکی ہے', noNotes: 'کوئی نوٹ درج نہیں', dateUnavailable: 'تاریخ درج نہیں',
      deleteReminder: 'حذف کریں', deleteTitle: 'یہ یاد دہانی حذف کرنی ہے؟', deleteMessage: 'یہ یاد دہانی فہرست سے ختم ہو جائے گی:', keepReminder: 'یاد دہانی رہنے دیں', confirmDelete: 'ہاں، حذف کریں', deleting: 'حذف ہو رہی ہے…', deleteFailed: 'یاد دہانی حذف نہیں ہو سکی۔ دوبارہ کوشش کریں۔', reminderDeleted: 'یاد دہانی حذف ہو گئی۔',
      missingTitle: 'جانور کا ریکارڈ نہیں ملا', missingMessage: 'یاد دہانیاں دیکھنے کے لیے درست جانور منتخب کریں۔', notFoundTitle: 'جانور کا ریکارڈ نہیں ملا', notFoundMessage: 'یہ جانور موجود نہیں یا اس کا ریکارڈ حذف ہو چکا ہے۔',
      forbiddenTitle: 'اجازت نہیں ہے', forbiddenMessage: 'آپ کو یہ ریکارڈ دیکھنے کی اجازت نہیں ہے۔', connectionTitle: 'یاد دہانیاں ابھی دستیاب نہیں', connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔', malformedTitle: 'یاد دہانیاں مکمل نہیں دکھائی جا سکتیں', malformedMessage: 'محفوظ معلومات کی شکل سمجھ نہیں آئی۔ براہِ کرم دوبارہ کوشش کریں۔',
      footerCare: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔', footerReminder: 'وقت پر دیکھ بھال کی تاریخیں یاد رکھیں۔'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language', logout: 'Logout', backToProfile: 'Back to Animal Profile',
      loadingLabel: 'Loading preventive-care reminders', tryAgain: 'Try again', pageTitle: 'Preventive Care / Reminders', pageSubtitle: 'Keep vaccination, deworming and routine check-up dates in one place.',
      addReminder: 'Add Reminder', careSchedule: 'Care schedule', allReminders: 'All Reminders', reminderCount: '{count} reminders', oneReminder: '1 reminder',
      emptyTitle: 'No preventive-care reminders yet.', emptyHelp: 'Add the next vaccination, deworming or routine check-up date.',
      reminderDistinction: 'These are reminders only. They are not medical records proving that a vaccination or treatment was completed.', preventiveCare: 'Preventive care', formHelp: 'Record the date of this animal’s next planned care.',
      reminderType: 'Reminder Type', typePlaceholder: 'e.g. Vaccination', typeHelp: 'You can enter any short reminder name that fits your needs.', dueDate: 'Due Date', notes: 'Notes (optional)', notesPlaceholder: 'e.g. Previous dose or veterinarian’s instruction', notesHelp: 'Your note will be saved exactly as entered.',
      cancel: 'Cancel', saveReminder: 'Save Reminder', saving: 'Saving…', closeFormLabel: 'Close form', typeRequired: 'Please enter a reminder type.', dateRequired: 'Please select a due date.',
      reminderSaved: 'Reminder saved.', createFailed: 'The reminder could not be saved. Please check the information and try again.',
      upcoming: 'Upcoming', dueToday: 'Due today', overdue: 'Overdue', noNotes: 'No notes recorded', dateUnavailable: 'Date not recorded',
      deleteReminder: 'Delete', deleteTitle: 'Delete this reminder?', deleteMessage: 'This reminder will be removed from the list:', keepReminder: 'Keep reminder', confirmDelete: 'Yes, delete', deleting: 'Deleting…', deleteFailed: 'The reminder could not be deleted. Please try again.', reminderDeleted: 'Reminder deleted.',
      missingTitle: 'Animal record not found', missingMessage: 'Select a valid animal to view its reminders.', notFoundTitle: 'Animal record not found', notFoundMessage: 'This animal does not exist or its record may have been removed.',
      forbiddenTitle: 'Permission required', forbiddenMessage: 'You do not have permission to access this record.', connectionTitle: 'Reminders unavailable right now', connectionMessage: 'We could not connect. Please try again in a little while.', malformedTitle: 'Reminders cannot be shown completely', malformedMessage: 'Some saved information could not be understood. Please try again.',
      footerCare: 'Built to support better livestock care.', footerReminder: 'Keep important care dates easy to remember.'
    }
  };

  const el = {
    loading: document.querySelector('#care-loading'), error: document.querySelector('#care-error'), page: document.querySelector('#care-page'),
    errorTitle: document.querySelector('#care-error-title'), errorMessage: document.querySelector('#care-error-message'), retry: document.querySelector('#retry-care'),
    profileLink: document.querySelector('#profile-link'), errorProfileLink: document.querySelector('#error-profile-link'), animalIcon: document.querySelector('#animal-icon'), animalSummary: document.querySelector('#animal-summary'),
    list: document.querySelector('#reminder-list'), empty: document.querySelector('#reminders-empty'), count: document.querySelector('#reminder-count'), feedback: document.querySelector('#page-feedback'),
    reminderDialog: document.querySelector('#reminder-dialog'), reminderForm: document.querySelector('#reminder-form'), reminderAlert: document.querySelector('#reminder-alert'), saveReminder: document.querySelector('#save-reminder'), reminderTypeInput: document.querySelector('[name="reminder_type"]'), reminderTypeSuggestions: document.querySelector('#reminder-type-suggestions'),
    deleteDialog: document.querySelector('#delete-reminder-dialog'), deleteName: document.querySelector('#delete-reminder-name'), deleteAlert: document.querySelector('#delete-alert'), confirmDelete: document.querySelector('#confirm-delete-reminder')
  };

  let language = window.MaweshiI18n.getLanguage();
  let animal = null;
  let reminders = [];
  let state = 'loading';
  let errorKind = null;
  let deleteTarget = null;

  function t(key) { return copy[language][key] || key; }
  function hasValue(value) { return value !== null && value !== undefined && String(value).trim() !== ''; }
  function reminderTypeLabel(value) { return window.MaweshiI18n.reminderTypeLabel(value, language); }

  function updateReminderTypeChoices() {
    const currentValue = el.reminderTypeInput.value;
    const standardValues = new Set(['Vaccination', 'Deworming', 'Routine check-up']);
    el.reminderTypeSuggestions.querySelectorAll('[data-reminder-type]').forEach((option) => {
      option.value = reminderTypeLabel(option.dataset.reminderType);
    });
    const canonicalValue = window.MaweshiI18n.reminderTypeValue(currentValue);
    if (standardValues.has(canonicalValue)) el.reminderTypeInput.value = reminderTypeLabel(canonicalValue);
  }

  const api = {
    getAnimal: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}`, { headers: { Accept: 'application/json' } }),
    getReminders: (id) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/reminders`, { headers: { Accept: 'application/json' } }),
    createReminder: (id, payload) => window.MaweshiAuth.request(`${API_BASE}/api/animals/${encodeURIComponent(id)}/reminders`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload)
    }),
    deleteReminder: (id) => window.MaweshiAuth.request(`${API_BASE}/api/reminders/${encodeURIComponent(id)}`, { method: 'DELETE', headers: { Accept: 'application/json' } })
  };

  function profileUrl() {
    return animalId && animalId.trim() ? `animal-profile.html?id=${encodeURIComponent(animalId)}` : 'dashboard.html';
  }

  function animalTypeIcon(type) {
    const value = hasValue(type) ? String(type).toLowerCase() : '';
    if (value.includes('buffalo') || value.includes('بھینس')) return '🐃';
    if (value.includes('goat') || value.includes('بکری') || value.includes('بکرا')) return '🐐';
    if (value.includes('sheep') || value.includes('بھیڑ') || value.includes('دنب')) return '🐑';
    if (value.includes('cow') || value.includes('cattle') || value.includes('گائے') || value.includes('بیل')) return '🐄';
    return '🐾';
  }

  function parseDueDate(raw) {
    if (typeof raw !== 'string' || !raw.trim()) return null;
    const value = raw.trim();
    const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
    const date = dateOnly
      ? new Date(Number(dateOnly[1]), Number(dateOnly[2]) - 1, Number(dateOnly[3]))
      : new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function startOfDay(date) { return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime(); }

  function dueState(raw) {
    const due = parseDueDate(raw);
    if (!due) return 'upcoming';
    const difference = startOfDay(due) - startOfDay(new Date());
    if (difference < 0) return 'overdue';
    if (difference === 0) return 'today';
    return 'upcoming';
  }

  function dueTimestamp(raw) {
    const date = parseDueDate(raw);
    return date ? date.getTime() : Number.MAX_SAFE_INTEGER;
  }

  function formatDueDate(raw) {
    const date = parseDueDate(raw);
    if (!date) return t('dateUnavailable');
    const includeTime = typeof raw === 'string' && raw.includes('T');
    const options = includeTime ? { dateStyle: 'medium', timeStyle: 'short' } : { dateStyle: 'medium' };
    return new Intl.DateTimeFormat(language === 'ur' ? 'ur-PK' : 'en-PK', options).format(date);
  }

  function stateInfo(raw) {
    const status = dueState(raw);
    if (status === 'overdue') return { key: status, label: t('overdue'), icon: '!' };
    if (status === 'today') return { key: status, label: t('dueToday'), icon: '•' };
    return { key: status, label: t('upcoming'), icon: '✓' };
  }

  function validReminder(record) {
    return record && typeof record === 'object' && hasValue(record.id) && hasValue(record.reminder_type) && hasValue(record.due_date);
  }

  function sortedReminders(records) {
    return [...records].sort((a, b) => dueTimestamp(a.due_date) - dueTimestamp(b.due_date));
  }

  function showFeedback(message) {
    el.feedback.textContent = message;
    el.feedback.classList.remove('hidden');
    window.clearTimeout(showFeedback.timer);
    showFeedback.timer = window.setTimeout(() => el.feedback.classList.add('hidden'), 4500);
  }

  function createReminderItem(record) {
    const item = document.createElement('article');
    item.className = 'reminder-item';

    const dateArea = document.createElement('div'); dateArea.className = 'reminder-date';
    const dateMark = document.createElement('span'); dateMark.className = 'reminder-date-mark'; dateMark.textContent = '📅'; dateMark.setAttribute('aria-hidden', 'true');
    const dateCopy = document.createElement('div');
    const time = document.createElement('time'); time.dateTime = record.due_date; time.textContent = formatDueDate(record.due_date);
    const status = stateInfo(record.due_date);
    const statusLabel = document.createElement('span'); statusLabel.className = `reminder-state reminder-state--${status.key}`; statusLabel.textContent = `${status.icon} ${status.label}`;
    dateCopy.append(time, statusLabel); dateArea.append(dateMark, dateCopy);

    const content = document.createElement('div'); content.className = 'reminder-content';
    const title = document.createElement('h3'); title.textContent = reminderTypeLabel(record.reminder_type); title.dir = 'auto';
    const notes = document.createElement('p'); notes.textContent = hasValue(record.notes) ? record.notes : t('noNotes'); notes.dir = 'auto';
    content.append(title, notes);

    const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'reminder-delete'; remove.dataset.deleteReminder = String(record.id); remove.textContent = t('deleteReminder');
    item.append(dateArea, content, remove);
    return item;
  }

  function renderHeader() {
    if (!animal) return;
    el.animalIcon.textContent = animalTypeIcon(animal.animal_type);
    el.animalSummary.textContent = [animal.name, animal.animal_type].filter(hasValue).join(' · ');
    document.title = `${t('pageTitle')} · ${animal.name || ''} | Maweshi Muhafiz`;
  }

  function renderReminders() {
    const ordered = sortedReminders(reminders);
    el.list.replaceChildren(...ordered.map(createReminderItem));
    el.list.classList.toggle('hidden', ordered.length === 0);
    el.empty.classList.toggle('hidden', ordered.length !== 0);
    el.count.textContent = ordered.length === 1 ? t('oneReminder') : t('reminderCount').replace('{count}', new Intl.NumberFormat(language === 'ur' ? 'ur-PK' : 'en-PK').format(ordered.length));
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
    if (state === 'ready') {
      renderHeader();
      renderReminders();
    }
  }

  function errorType(error) {
    if (error?.status === 404) return 'notFound';
    if (error?.status === 403) return 'forbidden';
    return 'connection';
  }

  async function loadCare() {
    if (!animalId || !animalId.trim()) {
      state = 'error'; errorKind = 'missing'; render(); return;
    }
    state = 'loading'; errorKind = null; render();
    try {
      const [animalRecord, reminderRecords] = await Promise.all([api.getAnimal(animalId), api.getReminders(animalId)]);
      if (!animalRecord || typeof animalRecord !== 'object' || !Array.isArray(reminderRecords)) {
        state = 'error'; errorKind = 'malformed'; render(); return;
      }
      animal = animalRecord;
      reminders = reminderRecords.filter(validReminder);
      state = 'ready'; render();
    } catch (error) {
      console.error('Preventive-care reminders could not be loaded.', error);
      state = 'error'; errorKind = errorType(error); render();
    }
  }

  function openReminderForm() {
    el.reminderForm.reset();
    el.reminderAlert.classList.add('hidden');
    el.reminderDialog.showModal();
  }

  function reminderPayload() {
    const data = new FormData(el.reminderForm);
    const payload = {
      reminder_type: window.MaweshiI18n.reminderTypeValue(data.get('reminder_type')),
      due_date: String(data.get('due_date') || '').trim()
    };
    const notes = String(data.get('notes') || '').trim();
    if (notes) payload.notes = notes;
    return payload;
  }

  function validateReminder(payload) {
    if (!payload.reminder_type) return t('typeRequired');
    if (!payload.due_date) return t('dateRequired');
    return '';
  }

  async function submitReminder(event) {
    event.preventDefault();
    el.reminderAlert.classList.add('hidden');
    const payload = reminderPayload();
    const validationMessage = validateReminder(payload);
    if (validationMessage) {
      el.reminderAlert.textContent = validationMessage;
      el.reminderAlert.classList.remove('hidden');
      return;
    }

    el.saveReminder.disabled = true;
    el.saveReminder.textContent = t('saving');
    try {
      const created = await api.createReminder(animalId, payload);
      if (!validReminder(created)) throw new Error('Reminder response was incomplete.');
      reminders.push(created);
      el.reminderDialog.close();
      renderReminders();
      showFeedback(t('reminderSaved'));
    } catch (error) {
      console.error('Reminder could not be created.', error);
      el.reminderAlert.textContent = t('createFailed');
      el.reminderAlert.classList.remove('hidden');
    } finally {
      el.saveReminder.disabled = false;
      el.saveReminder.textContent = t('saveReminder');
    }
  }

  function openDeleteReminder(id) {
    deleteTarget = reminders.find((record) => String(record.id) === String(id)) || null;
    if (!deleteTarget) return;
    el.deleteName.textContent = reminderTypeLabel(deleteTarget.reminder_type);
    el.deleteAlert.classList.add('hidden');
    el.deleteDialog.showModal();
  }

  async function deleteReminder() {
    if (!deleteTarget) return;
    el.deleteAlert.classList.add('hidden');
    el.confirmDelete.disabled = true;
    el.confirmDelete.textContent = t('deleting');
    try {
      await api.deleteReminder(deleteTarget.id);
      reminders = reminders.filter((record) => String(record.id) !== String(deleteTarget.id));
      deleteTarget = null;
      el.deleteDialog.close();
      renderReminders();
      showFeedback(t('reminderDeleted'));
    } catch (error) {
      console.error('Reminder could not be deleted.', error);
      el.deleteAlert.textContent = t('deleteFailed');
      el.deleteAlert.classList.remove('hidden');
    } finally {
      el.confirmDelete.disabled = false;
      el.confirmDelete.textContent = t('confirmDelete');
    }
  }

  function closeDialog(button) {
    const dialog = button.closest('dialog');
    if (dialog) dialog.close();
  }

  function applyLanguage(nextLanguage) {
    language = window.MaweshiI18n.applyPage(nextLanguage, copy).language;
    updateReminderTypeChoices();
    render();
    if (deleteTarget) el.deleteName.textContent = reminderTypeLabel(deleteTarget.reminder_type);
  }

  const destination = profileUrl();
  el.profileLink.href = destination;
  el.errorProfileLink.href = destination;

  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) applyLanguage(languageButton.dataset.language);
    if (event.target.closest('[data-open-reminder]')) openReminderForm();
    const deleteButton = event.target.closest('[data-delete-reminder]');
    if (deleteButton) openDeleteReminder(deleteButton.dataset.deleteReminder);
    const closeButton = event.target.closest('[data-close-dialog]');
    if (closeButton) closeDialog(closeButton);
  });

  document.querySelectorAll('dialog').forEach((dialog) => dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  }));
  el.retry.addEventListener('click', loadCare);
  el.reminderForm.addEventListener('submit', submitReminder);
  el.confirmDelete.addEventListener('click', deleteReminder);

  applyLanguage(language);
  loadCare();
})();
