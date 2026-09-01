(() => {
  'use strict';

  const API = {
  login: 'http://127.0.0.1:5000/api/auth/login',
  signup: 'http://127.0.0.1:5000/api/auth/signup'
};
  const DASHBOARD_URL = 'index.html';
  const EMAIL_PATTERN = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

  const messages = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', mainNavigation: 'مرکزی فہرست', homeLabel: 'مویشی محافظ کے مرکزی صفحے پر جائیں', languageLabel: 'زبان منتخب کریں', backHome: 'مرکزی صفحہ',
      eyebrow: 'مویشیوں کی دیکھ بھال، ایک محفوظ جگہ پر', introTitle: 'اپنے جانوروں کا ریکارڈ آسانی سے سنبھالیں۔',
      introText: 'لاگ اِن کریں یا نیا اکاؤنٹ بنائیں تاکہ جانوروں کی معلومات اور صحت کا ریکارڈ ایک جگہ محفوظ رہے۔',
      benefitRecords: 'ہر جانور کا منظم ریکارڈ', benefitGuidance: 'سادہ اردو میں صحت کی رہنمائی', benefitHistory: 'صحت کی پچھلی معلومات ایک جگہ',
      safetyNote: 'اپنا پاس ورڈ کسی دوسرے شخص کے ساتھ شیئر نہ کریں۔', authOptions: 'اکاؤنٹ کے اختیارات', login: 'لاگ اِن', createAccount: 'اکاؤنٹ بنائیں',
      welcomeBack: 'خوش آمدید', loginHeading: 'اپنے اکاؤنٹ میں لاگ اِن کریں', loginHelp: 'اپنے جانوروں کے ریکارڈ تک پہنچنے کے لیے معلومات درج کریں۔',
      startToday: 'آج ہی شروعات کریں', signupHeading: 'اپنا اکاؤنٹ بنائیں', signupHelp: 'صرف ضروری معلومات درج کریں۔',
      name: 'نام', email: 'ای میل', password: 'پاس ورڈ', confirmPassword: 'پاس ورڈ دوبارہ لکھیں', namePlaceholder: 'اپنا نام لکھیں', emailPlaceholder: 'name@example.com',
      passwordPlaceholder: 'اپنا پاس ورڈ لکھیں', newPasswordPlaceholder: 'کم از کم 8 حروف', confirmPasswordPlaceholder: 'وہی پاس ورڈ دوبارہ لکھیں',
      passwordHelp: 'پاس ورڈ کم از کم 8 حروف کا ہونا چاہیے۔', show: 'دکھائیں', hide: 'چھپائیں', showPassword: 'پاس ورڈ دکھائیں', hidePassword: 'پاس ورڈ چھپائیں',
      newHere: 'نئے صارف ہیں؟', alreadyAccount: 'پہلے سے اکاؤنٹ ہے؟', loggingIn: 'لاگ اِن ہو رہا ہے…', creatingAccount: 'اکاؤنٹ بن رہا ہے…',
      loginSuccess: 'لاگ اِن کامیاب ہو گیا۔', signupSuccess: 'اکاؤنٹ بن گیا۔', nameRequired: 'براہِ کرم اپنا نام لکھیں۔', nameTooLong: 'نام 100 حروف سے زیادہ نہیں ہو سکتا۔',
      emailRequired: 'براہِ کرم اپنی ای میل لکھیں۔', emailInvalid: 'براہِ کرم درست ای میل لکھیں۔', passwordRequired: 'براہِ کرم پاس ورڈ لکھیں۔',
      passwordTooShort: 'پاس ورڈ کم از کم 8 حروف کا ہونا چاہیے۔', passwordsMismatch: 'دونوں پاس ورڈ ایک جیسے ہونے چاہییں۔', invalidCredentials: 'ای میل یا پاس ورڈ درست نہیں۔',
      duplicateEmail: 'اس ای میل سے اکاؤنٹ پہلے ہی موجود ہے۔', signupFailed: 'اکاؤنٹ نہیں بن سکا۔ معلومات دیکھ کر دوبارہ کوشش کریں۔', loginFailed: 'لاگ اِن نہیں ہو سکا۔ دوبارہ کوشش کریں۔',
      connectionUnavailable: 'رابطہ دستیاب نہیں۔ کچھ دیر بعد دوبارہ کوشش کریں۔', unexpectedResponse: 'جواب سمجھ نہیں آیا۔ دوبارہ کوشش کریں۔',
      sessionExpired: 'آپ کا سیشن ختم ہو گیا ہے۔ براہِ کرم دوبارہ لاگ اِن کریں۔', loginRequired: 'اپنے جانوروں کا ریکارڈ دیکھنے کے لیے لاگ اِن کریں۔', footerLine: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔'
    },
    en: {
      skipLink: 'Skip to main content', mainNavigation: 'Main navigation', homeLabel: 'Go to the Maweshi Muhafiz home page', languageLabel: 'Choose language', backHome: 'Home',
      eyebrow: 'Livestock care, kept in one trusted place', introTitle: 'Keep your animals’ records clearly organised.',
      introText: 'Log in or create an account to keep animal details and health records together in one place.',
      benefitRecords: 'An organised record for every animal', benefitGuidance: 'Clear health guidance in simple Urdu', benefitHistory: 'Health history kept together',
      safetyNote: 'Do not share your password with anyone else.', authOptions: 'Account options', login: 'Login', createAccount: 'Create Account',
      welcomeBack: 'Welcome back', loginHeading: 'Log in to your account', loginHelp: 'Enter your details to reach your animal records.',
      startToday: 'Start today', signupHeading: 'Create your account', signupHelp: 'Enter only the essential information.',
      name: 'Name', email: 'Email', password: 'Password', confirmPassword: 'Confirm password', namePlaceholder: 'Enter your name', emailPlaceholder: 'name@example.com',
      passwordPlaceholder: 'Enter your password', newPasswordPlaceholder: 'At least 8 characters', confirmPasswordPlaceholder: 'Enter the same password again',
      passwordHelp: 'Your password must be at least 8 characters.', show: 'Show', hide: 'Hide', showPassword: 'Show password', hidePassword: 'Hide password',
      newHere: 'New here?', alreadyAccount: 'Already have an account?', loggingIn: 'Logging in…', creatingAccount: 'Creating account…',
      loginSuccess: 'Login successful.', signupSuccess: 'Your account was created.', nameRequired: 'Please enter your name.', nameTooLong: 'Name cannot be longer than 100 characters.',
      emailRequired: 'Please enter your email.', emailInvalid: 'Please enter a valid email address.', passwordRequired: 'Please enter your password.',
      passwordTooShort: 'Password must be at least 8 characters.', passwordsMismatch: 'The passwords must match.', invalidCredentials: 'Email or password is incorrect.',
      duplicateEmail: 'An account already exists for this email.', signupFailed: 'We could not create your account. Please check the information and try again.', loginFailed: 'We could not log you in. Please try again.',
      connectionUnavailable: 'Connection unavailable. Please try again.', unexpectedResponse: 'We could not understand the response. Please try again.',
      sessionExpired: 'Your session has expired. Please log in again.', loginRequired: 'Please log in to view your animal records.', footerLine: 'Built to support better livestock care.'
    }
  };

  const el = {
    loginTab: document.querySelector('#login-tab'), signupTab: document.querySelector('#signup-tab'), loginView: document.querySelector('#login-view'), signupView: document.querySelector('#signup-view'),
    loginForm: document.querySelector('#login-form'), signupForm: document.querySelector('#signup-form'), loginSubmit: document.querySelector('#login-submit'), signupSubmit: document.querySelector('#signup-submit'),
    feedback: document.querySelector('#auth-feedback')
  };
  let language = window.MaweshiI18n.getLanguage();
  const initialParams = new URLSearchParams(window.location.search);
  let activeView = initialParams.get('view') === 'signup' ? 'signup' : 'login';
  const initialReason = initialParams.get('reason');
  let submitting = false;

  function t(key) { return messages[language][key] || key; }

  function applyLanguage(nextLanguage) {
    language = window.MaweshiI18n.applyPage(nextLanguage, messages).language;
    document.title = `Maweshi Muhafiz | ${activeView === 'signup' ? t('createAccount') : t('login')}`;
    document.querySelectorAll('[data-toggle-password]').forEach(updatePasswordToggle);
  }

  function setView(view, focusTab = false) {
    activeView = view === 'signup' ? 'signup' : 'login';
    const isLogin = activeView === 'login';
    el.loginView.classList.toggle('hidden', !isLogin);
    el.signupView.classList.toggle('hidden', isLogin);
    el.loginTab.setAttribute('aria-selected', String(isLogin));
    el.signupTab.setAttribute('aria-selected', String(!isLogin));
    el.loginTab.tabIndex = isLogin ? 0 : -1;
    el.signupTab.tabIndex = isLogin ? -1 : 0;
    window.history.replaceState(null, '', `?view=${activeView}`);
    hideFeedback();
    document.title = `Maweshi Muhafiz | ${isLogin ? t('login') : t('createAccount')}`;
    if (focusTab) (isLogin ? el.loginTab : el.signupTab).focus();
  }

  function showFeedback(message, success = false) {
    el.feedback.textContent = message;
    el.feedback.classList.remove('hidden');
    el.feedback.classList.toggle('auth-feedback--success', success);
  }

  function hideFeedback() {
    el.feedback.textContent = '';
    el.feedback.classList.add('hidden');
    el.feedback.classList.remove('auth-feedback--success');
  }

  function updatePasswordToggle(button) {
    const input = button.closest('.password-control').querySelector('input');
    const visible = input.type === 'text';
    button.querySelector('span').textContent = t(visible ? 'hide' : 'show');
    button.setAttribute('aria-label', t(visible ? 'hidePassword' : 'showPassword'));
  }

  function togglePassword(button) {
    const input = button.closest('.password-control').querySelector('input');
    input.type = input.type === 'password' ? 'text' : 'password';
    updatePasswordToggle(button);
  }

  function validateLogin(form) {
    const email = form.elements.namedItem('email').value.trim();
    const password = form.elements.namedItem('password').value;
    if (!email) return t('emailRequired');
    if (!password) return t('passwordRequired');
    return null;
  }

  function validateSignup(form) {
    const name = form.elements.namedItem('name').value.trim();
    const email = form.elements.namedItem('email').value.trim();
    const password = form.elements.namedItem('password').value;
    if (!name) return t('nameRequired');
    if (name.length > 100) return t('nameTooLong');
    if (!email) return t('emailRequired');
    if (email.length > 254 || !EMAIL_PATTERN.test(email)) return t('emailInvalid');
    if (!password) return t('passwordRequired');
    if (password.length < 8) return t('passwordTooShort');
    if (password !== form.elements.namedItem('confirm_password').value) return t('passwordsMismatch');
    return null;
  }

  function friendlyServerError(payload, status, operation) {
    const details = Array.isArray(payload?.error) ? payload.error.join(' ') : String(payload?.error || payload?.message || '');
    const lower = details.toLowerCase();
    if (status === 401) return t('invalidCredentials');
    if (status === 409 || lower.includes('already registered')) return t('duplicateEmail');
    if (lower.includes("'name' is required")) return t('nameRequired');
    if (lower.includes("'email' is required")) return t('emailRequired');
    if (lower.includes('valid email')) return t('emailInvalid');
    if (lower.includes("'password' is required")) return t('passwordRequired');
    if (lower.includes('at least 8')) return t('passwordTooShort');
    return t(operation === 'signup' ? 'signupFailed' : 'loginFailed');
  }

  async function submitAuth(operation, form, button) {
    if (submitting) return;
    const validationMessage = operation === 'signup' ? validateSignup(form) : validateLogin(form);
    if (validationMessage) { showFeedback(validationMessage); return; }

    const payload = operation === 'signup'
      ? {
          name: form.elements.namedItem('name').value.trim(),
          email: form.elements.namedItem('email').value.trim(),
          password: form.elements.namedItem('password').value
        }
      : {
          email: form.elements.namedItem('email').value.trim(),
          password: form.elements.namedItem('password').value
        };

    submitting = true;
    hideFeedback();
    button.disabled = true;
    button.textContent = t(operation === 'signup' ? 'creatingAccount' : 'loggingIn');

    try {
      const response = await fetch(API[operation], {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      let body;
      try { body = await response.json(); }
      catch { throw new Error('unreadable-response'); }

      if (!response.ok || body?.success !== true) {
        showFeedback(friendlyServerError(body, response.status, operation));
        return;
      }
      if (!body.data?.token || !body.data?.user) throw new Error('unreadable-response');

      window.MaweshiAuth.saveSession(body.data.token, body.data.user);
      showFeedback(t(operation === 'signup' ? 'signupSuccess' : 'loginSuccess'), true);
      window.setTimeout(() => { window.location.href = DASHBOARD_URL; }, 500);
    } catch (error) {
      console.error('Authentication request could not be completed.', error);
      showFeedback(error.message === 'unreadable-response' ? t('unexpectedResponse') : t('connectionUnavailable'));
    } finally {
      submitting = false;
      button.disabled = false;
      button.textContent = t(operation === 'signup' ? 'createAccount' : 'login');
    }
  }

  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) applyLanguage(languageButton.dataset.language);
    const tab = event.target.closest('[data-auth-view]');
    if (tab) setView(tab.dataset.authView);
    const switchButton = event.target.closest('[data-switch-view]');
    if (switchButton) setView(switchButton.dataset.switchView, true);
    const passwordButton = event.target.closest('[data-toggle-password]');
    if (passwordButton) togglePassword(passwordButton);
  });

  el.loginForm.addEventListener('submit', (event) => { event.preventDefault(); submitAuth('login', el.loginForm, el.loginSubmit); });
  el.signupForm.addEventListener('submit', (event) => { event.preventDefault(); submitAuth('signup', el.signupForm, el.signupSubmit); });
  el.loginTab.addEventListener('keydown', (event) => { if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') setView('signup', true); });
  el.signupTab.addEventListener('keydown', (event) => { if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') setView('login', true); });

  applyLanguage(language);
  setView(activeView);
  if (initialReason === 'session-expired') showFeedback(t('sessionExpired'));
  else if (initialReason === 'login-required') showFeedback(t('loginRequired'));
})();
